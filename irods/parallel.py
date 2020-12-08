#!/usr/bin/env python
from __future__ import print_function

import os
import ssl
import json
import xml.etree.ElementTree as ET

import io
import time
import sys

from irods.data_object import iRODSDataObjectFileRaw
from irods.message import ( StringStringMap, FileOpenRequest,
                            GetFileDescriptorInfo, iRODSMessage )
from irods.api_number import api_number
import irods.keywords as kw
import concurrent.futures
import threading
import multiprocessing
from collections import OrderedDict
import six
from six.moves.queue import Queue,Full,Empty
import logging

logger = logging.getLogger( __name__ )
nullh  = logging.NullHandler()
logger.addHandler( nullh )

RECOMMENDED_NUM_THREADS_PER_TRANSFER = 3

SYNC_ON_FD_OPEN = True

verboseConnection = False


try:
    from threading import Barrier   #    with Python versions >= 3.2 
except ImportError:
    class Barrier(object):
        def __init__(self, n):
            """Initialize a Barrier to wait on n threads."""
            self.n = n
            self.count = 0
            self.mutex = threading.Semaphore(1)
            self.barrier = threading.Semaphore(0)
        def wait(self):
            """Per-thread wait function.
            As in Python3.2 threading, returns 0 <= wait_serial_int < n
            """
            self.mutex.acquire()
            self.count += 1
            count = self.count
            self.mutex.release()
            if count == self.n: self.barrier.release()
            self.barrier.acquire()
            self.barrier.release()
            return count - 1

class _db_Barrier(Barrier):
    """Slight modification of the Barrier construct. The aim is
    to return 0 from wait() for the thread that creates the Barrier.
    """
    def __init__(self,*a,**k):
        self.__tids = OrderedDict([(threading.currentThread(),0)])
        self.__lock = threading.Lock()
        super(_db_Barrier,self).__init__(*a,**k)
    def wait(self,*a,**k):
        serial = super(_db_Barrier,self).wait(*a,**k)
        with self.__lock:
            tid = threading.currentThread()
            next_i = len(self.__tids)
            return self.__tids.setdefault(tid,next_i)


class BadCallbackTarget(TypeError): pass


class AsyncNotify (object):

    """A type returned when the PUT or GET operation passed includes NONBLOCKING.
       If enabled, the callback function (or callable object) will be triggered
       when all parts of the parallel transfer are complete.  It should accept
       exactly one argument, the irods.parallel.AsyncNotify instance that
       is calling it.
    """

    def set_transfer_done_callback( self, callback ):
        if callback is not None:
            if not callable(callback):
                raise BadCallbackTarget( '"callback" must be a callable accepting at least 1 argument' )
        self.done_callback = callback

    def __init__(self, futuresList, callback = None, progress_Queue = None, total = None, keep_ = ()):
        self._futures = set(futuresList)
        self._futures_done = dict()
        self.keep = dict(keep_)
        self._lock = threading.Lock()
        self.set_transfer_done_callback (callback)
        self.__done = False
        if self._futures:
            for future in self._futures: future.add_done_callback( self )
        else:
            self.__invoke_done_callback()

        self.progress = [0, 0]
        if (progress_Queue) and (total is not None):
            self.progress[1] = total
            def _progress(Q,this):  # - thread to update progress indicator
                while this.progress[0] < this.progress[1]:
                    i = None
                    try:
                        i = Q.get(timeout=0.1)
                    except Empty:
                        pass
                    if i is not None:
                        if isinstance(i,six.integer_types) and i >= 0: this.progress[0] += i
                        else: break
            self._progress_fn = _progress
            self._progress_thread = threading.Thread( target = self._progress_fn, args = (progress_Queue, self))
            self._progress_thread.start()

    @staticmethod
    def asciiBar( lst, memo = [1] ):
        memo[0] += 1
        spinner = "|/-\\"[memo[0]%4]
        percent = "%5.1f%%"%(lst[0]*100.0/lst[1])
        mbytes = "%9.1f MB / %9.1f MB"%(lst[0]/1e6,lst[1]/1e6)
        if lst[1] != 0:
            s = "  {spinner} {percent} [ {mbytes} ] "
        else:
            s = "  {spinner} "
        return s.format(**locals())

    def wait_until_transfer_done (self, timeout=float('inf'), progressBar = False):
        carriageReturn = '\r'
        begin = t = time.time()
        end = begin + timeout
        while not self.__done:
            time.sleep(min(0.1, max(0.0, end - t)))
            t = time.time()
            if t >= end: break
            if progressBar:
                print ('  ' + self.asciiBar( self.progress ) + carriageReturn, end='', file=sys.stderr)
                sys.stderr.flush()
        return self.__done

    def __call__(self,future): # Our instance is called by each future (individual file part) when done.
                               # When all futures are done, we invoke the configured callback.
        with self._lock:
            self._futures_done[future] = future.result()
            if len(self._futures) == len(self._futures_done): self.__invoke_done_callback()

    def __invoke_done_callback(self):
        try:
            if callable(self.done_callback): self.done_callback(self)
        finally:
            self.keep.pop('data_raw',None)
            self.__done = True
        self.set_transfer_done_callback(None)

    @property
    def futures(self): return list(self._futures)

    @property
    def futures_done(self): return dict(self._futures_done)


class Oper(object):

    """A custom enum-type class with utility methods.  """

    GET = 0
    PUT = 1
    NONBLOCKING = 2

    def __int__(self): return self._opr
    def __init__(self, rhs): self._opr = int(rhs)
    def isPut(self): return 0 != (self._opr & self.PUT)
    def isGet(self): return not self.isPut()
    def isNonBlocking(self): return 0 != (self._opr & self.NONBLOCKING)

    def data_object_mode(self):
        if self.isPut():
            return 'w'
        else:
            return 'r'

    def disk_file_mode(self, initial_open = False, binary = True):
        if self.isPut():
            mode = 'r'
        else:
            mode = 'w' if initial_open else 'r+'
        return ((mode + 'b') if binary else mode)


# -- Helper functions --

def _data_obj_get_filedesc_info (conn, data_object, opr_, target_resc = '', memo = None  ):
    OPEN_options = {}
    if target_resc:
        OPEN_options[ kw.RESC_NAME_KW ] = target_resc
        OPEN_options[ kw.DEST_RESC_NAME_KW ] = target_resc
    Operation = Oper(opr_)

    io_obj = data_object.open( Operation.data_object_mode(), **OPEN_options )
    FD = io_obj.raw.desc
    buf_ = json.dumps({'fd': FD})
    buf_len_ = len(buf_)
    message_body = GetFileDescriptorInfo (buf = buf_ , buflen = buf_len_)
    message = iRODSMessage('RODS_API_REQ', msg=message_body,
                           int_info=api_number['GET_FILE_DESCRIPTOR_INFO_APN'])
    conn.send(message)
    try:
        result_message = conn.recv()
    except Exception:
        print ("Couldn't receive or process response to GET_FILE_DESCRIPTOR_INFO_APN")
        raise
    if memo is not None: memo.append( io_obj )
    return result_message


def _io_send_bytes_progress (queueObject, item):
    try:
        queueObject.put(item)
        return True
    except Full:
        return False

COPY_BUF_SIZE = (1024 ** 2) * 4

def _copy_part( src, dst, length, queueObject, debug_info):
    bytecount = 0
    accum = 0
    while True and bytecount < length:
        buf = src.read(min(COPY_BUF_SIZE, length - bytecount))
        buf_len = len(buf)
        if 0 == buf_len: break
        dst.write(buf)
        bytecount += buf_len
        accum += buf_len
        if queueObject and accum and _io_send_bytes_progress(queueObject,accum): accum = 0
        if verboseConnection:
            print ("("+debug_info+")",end='',file=sys.stderr); sys.stderr.flush()
    src.close()
    dst.close()
    return bytecount


def _io_part (session_, d_path, range_ , file_ , opr_, hierarchy_str, token = '', 
              queueObject = None, _barrier = None):
    if 0 == len(range_): return 0
    options = {}
    if hierarchy_str:
        options[ kw.RESC_HIER_STR_KW ] = hierarchy_str
    if token:
        options[ kw.REPLICA_TOKEN_KW ] = token

    Operation = Oper(opr_)
    conn = session_.pool.get_connection()

    message_body = FileOpenRequest(
        objPath=d_path,
        openFlags=(os.O_WRONLY if Operation.isPut() else os.O_RDONLY),
        KeyValPair_PI=StringStringMap(options)
    )
    message = iRODSMessage('RODS_API_REQ', msg=message_body,
                           int_info=api_number['DATA_OBJ_OPEN_AN'])
    conn.send(message)
    desc = conn.recv().int_info
    objHandle = io.BufferedRandom(iRODSDataObjectFileRaw(conn, desc, **options))
    (start,length) = (range_[0], len(range_))
    objHandle.seek(start)
    file_.seek(start)

    thread_debug_info = str(threading.currentThread().ident)
    if _barrier: thread_debug_info = str( _barrier.wait() )  # wait() returns 1 .. N for the workers
    return _copy_part (file_,objHandle,length, queueObject, thread_debug_info) if Operation.isPut() \
      else _copy_part (objHandle,file_,length, queueObject, thread_debug_info)


def _io_multipart_threaded(operation_ , dataObj, replica_token, hier_str, session,  fname,
                           num_threads = 0,
                           range_for_io = None,
                           orig_conn = None,
                           **extra_options):
    """Called by _io_main.
    Carves up (0,total_bytes) range into `num_threads` pieces and manage the parts of the async transfer"""

    Operation = Oper( operation_ )

    with open(fname, Operation.disk_file_mode(initial_open=True)) as f:
        f.seek(0, os.SEEK_END)
        total_size = f.tell () if Operation.isPut() else \
                     dataObj.open(Operation.data_object_mode()).seek(0,os.SEEK_END)
    if num_threads < 1:
        num_threads = RECOMMENDED_NUM_THREADS_PER_TRANSFER
    num_threads = max(1, min(multiprocessing.cpu_count(), num_threads))
    P = 1 + (total_size // num_threads)
    logger.info( "num_threads = %s ; (P)artitionSize = %s" % (num_threads,P))
    ranges = [six.moves.range(i*P,min(i*P+P,total_size)) for i in range(num_threads) if i*P < total_size]
    bytecounts = []

    _queueLength = extra_options.get('_queueLength',0)
    if _queueLength > 0:
        queueObject = Queue(_queueLength)
    else:
        queueObject = None

    futures = []
    executor = concurrent.futures.ThreadPoolExecutor(max_workers = num_threads)
    if orig_conn is None:
        barrier = None
    else:
        barrier = _db_Barrier( 1 + len(ranges))
    for r in ranges:
        File = open( fname, Operation.disk_file_mode())
        futures.append(executor.submit( _io_part, session, dataObj.path, r, File, Operation, hier_str, replica_token, queueObject, _barrier=barrier))
    barrier.wait()
    if orig_conn: del orig_conn[0]

    if Operation.isNonBlocking():
        if _queueLength:
            return futures, queueObject, total_size
        else:
            return futures
    else:
        bytecounts = [ f.result() for f in futures ]
        return sum(bytecounts), total_size

# - _io_main
#    * determine replica information by:
#       - data path
#       - resc (R != '' if specified)

class WrongServerVersion (RuntimeError): pass

def io_main( session, d_path, opr_, fname, R='', **kwopt):

    Operation = Oper(opr_)
    Conn = session.pool._conn or session.pool.get_connection()
    iRODS_Version = list( Conn.server_version )

    if iRODS_Version < [4,2,8]:
        raise WrongServerVersion("Need iRODS server version of at least 4.2.8 for parallel transfer")

    R_libcall = kwopt.pop( 'target_resource_name', '')
    if R_libcall: R = R_libcall

    if Operation.isPut() and not( session.data_objects.exists(d_path) ):
        resc_options = {}
        if R:
            resc_options [kw.RESC_NAME_KW] = R
            resc_options [kw.DEST_RESC_NAME_KW] = R
            session.data_objects.create(d_path,**resc_options)

    d = session.data_objects.get( d_path )

    persist = []

    api_return = _data_obj_get_filedesc_info (session.pool._conn, d, Operation, target_resc = R, memo = persist)
    msg = api_return.msg
    Xml = ET.fromstring(msg.replace(b'\0',b''))
    dobj_info = json.loads(Xml.find('buf').text)

    replica_token = dobj_info.get("replica_token")
    resc_hier = ( dobj_info.get("data_object_info") or {} ).get("resource_hierarchy")

    logger.debug(json.dumps(dobj_info,indent=4))

    num_threads = kwopt.pop( 'num_threads', None)
    if num_threads is None: num_threads = int(kwopt.get('N','0'))

    # TODO: allow part of file or data object to be transferred (`range_for_io' param)

    queueLength = kwopt.get('queueLength',0)
    retval = _io_multipart_threaded (Operation, d, replica_token, resc_hier, session, fname, num_threads = num_threads, range_for_io = None,
                                     _queueLength = queueLength, orig_conn = (persist if (SYNC_ON_FD_OPEN and persist) else None))
    if queueLength > 0:
        (futures, chunk_notify_queue, total_bytes) = retval
    else:
        futures = retval
        chunk_notify_queue = total_bytes = None

    if Operation.isNonBlocking():
        return AsyncNotify( futures,                              # individual futures, one per transfer thread
                            progress_Queue = chunk_notify_queue,  # for notifying the progress indicator thread
                            total = total_bytes,                  # total number of bytes for parallel transfer
                            keep_ = {'data_raw': persist[:1]} )   # an open raw i/o object needing to be persisted, if any
    else:
        (_bytes_transferred, _bytes_total) = retval
        return (_bytes_transferred == _bytes_total)

if __name__ == '__main__':

    import getopt
    import atexit
    from irods.session import iRODSSession

    def setupLogging(name,level = logging.DEBUG):
        if nullh in logger.handlers:
            logger.removeHandler(nullh)
            if name:
                handler = logging.FileHandler(name)
            else:
                handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)-15s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel( level )

    try:
        env_file = os.environ['IRODS_ENVIRONMENT_FILE']
    except KeyError:
        env_file = os.path.expanduser('~/.irods/irods_environment.json')
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
    ssl_settings = {'ssl_context': ssl_context}
    sess = iRODSSession(irods_env_file=env_file, **ssl_settings)
    atexit.register(lambda : sess.cleanup())

    opt,arg = getopt.getopt( sys.argv[1:], 'vL:l:aR:N:')

    opts = dict(opt)

    logFilename = opts.pop('-L',None)  # '' for console, non-empty for filesystem destination
    logLevel = (logging.INFO if logFilename is None else logging.DEBUG)
    logFilename = logFilename or opts.pop('-l',None)
    if logFilename is not None: setupLogging(logFilename, logLevel)

    verboseConnection = (opts.pop('-v',None) is not None)

    async_xfer = opts.pop('-a',None)

    kwarg = { k.lstrip('-'):v for k,v in opts.items() }

    arg[1] = Oper.PUT if arg[1].lower() in ('w','put','a') \
                      else Oper.GET
    if async_xfer is not None:
        arg[1] |= Oper.NONBLOCKING

    ret = io_main(sess, *arg, **kwarg) # arg[0] = data object path
                                       # arg[1] = operation: or'd flags : [PUT|GET] NONBLOCKING
                                       # arg[2] = file path on local filesystem
                                       # kwarg['queueLength'] sets progress-queue length (0 if no progress indication needed)
                                       # kwarg can have 'N' (num threads) and 'R' (target resource name) via commandline
                                       # kwarg['num_threads'] (overrides 'N' when called as library)
                                       # kwarg['target_resource_name'] (overrides 'R' when called as library)
    if isinstance( ret, AsyncNotify ):
        print('waiting on completion...')
        ret.set_transfer_done_callback(lambda r: print('Async transfer done for:',r))
        done = ret.wait_until_transfer_done (timeout=10.0)  # - or do other useful work here
        if done:
            bytes_transferred = sum(ret.futures_done.values())
            print ('Asynch transfer complete. Total bytes transferred:', bytes_transferred)
        else:
            print ('Asynch transfer was not completed before timeout expired.')
    else:
        print('Synchronous transfer {}'.format('succeeded' if ret else 'failed'))

# Note : This module requires concurrent.futures, included in Python3.x.
#        On Python2.7, this dependency must be installed using 'pip install futures'.
# Demonstration :
#
# $ dd if=/dev/urandom bs=1k count=150000 of=$HOME/puttest
# $ time python -m irods.parallel -R demoResc -N 3 `ipwd`/test.dat put $HOME/puttest  # add -v,-a for verbose, asynch
# $ time python -m irods.parallel -R demoResc -N 3 `ipwd`/test.dat get $HOME/gettest  # add -v,-a for verbose, asynch
# $ diff puttest gettest
