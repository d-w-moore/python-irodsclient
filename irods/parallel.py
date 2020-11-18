#!/usr/bin/env python
from __future__ import print_function

import os
import ssl
import pprint
import sys
import json
import xml.etree.ElementTree as ET

import json
import getopt
import io
import ast

from irods.session import iRODSSession
from irods.pool import Pool
from irods.connection import Connection
from irods.message import FileOpenRequest
from irods.data_object import iRODSDataObjectFileRaw

from irods.message import (
    IntegerIntegerMap, IntegerStringMap, StringStringMap,
    FileOpenRequest, GetFileDescriptorInfo,
    iRODSMessage, GeneralAdminRequest)

from tempfile import NamedTemporaryFile
from irods.api_number import api_number
import irods.keywords as kw
import concurrent.futures
import threading
import six

import logging

logger = logging.getLogger( __name__ )
logger.addHandler( logging.StreamHandler())

class Opr:

    GET = 0
    PUT = 1

# -- command line option(s)

verbose = False

# -- helper functions

def _data_obj_get_filedesc_info (conn, data_object, mode = 'r', target_resc = '', junk = None  ):
    OPEN_options = {}
    if target_resc:
        OPEN_options[ kw.RESC_NAME_KW ] = target_resc

    io_obj = data_object.open(mode, create=False, **OPEN_options)
    FD = io_obj.raw.desc
    buf_ = json.dumps({'fd': FD})
    buf_len_ = len(buf_)
    message_body = GetFileDescriptorInfo (buf = buf_ , buflen = buf_len_)
    message = iRODSMessage('RODS_API_REQ', msg=message_body,
                           int_info=api_number['GET_FILE_DESCRIPTOR_INFO_APN'])
    conn.send(message)
    try:
        result_message = conn.recv()
    except Exception as e:
        print ("Couldn't receive or process response to GET_FILE_DESCRIPTOR_INFO_APN")
        raise
    if junk is not None: junk.append( io_obj )
    return result_message


COPY_BUF_SIZE = (1024 ** 2) * 4

def _copy_part( src, dst, length ):
    bytecount = 0
    while True and bytecount < length:
        buf = src.read(min(COPY_BUF_SIZE, length - bytecount))
        buf_len = len(buf)
        if 0 == buf_len: break
        dst.write(buf)
        bytecount += buf_len
    return bytecount

# -- worker thread

def io_part (session, d_path, range_ , file_ , opr, hierarchy_str, token='' ):
    if 0 == len(range_): return 0
    options = {}

    if hierarchy_str:
        options[ kw.RESC_HIER_STR_KW ] = hierarchy_str

    if token:
        options[ kw.REPLICA_TOKEN_KW ] = token

    a = session.pool.account
    p = Pool( a )
    conn = Connection (p, a)

    message_body = FileOpenRequest(
        objPath=d_path,
        openFlags=(os.O_RDONLY,os.O_WRONLY)[opr == Opr.PUT],
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
    return _copy_part (file_,objHandle,length) if opr == Opr.PUT \
      else _copy_part (objHandle,file_,length)


# -- called by io_main.
#    Carve up (0,total_bytes) range into `nthr` pieces and manage the parts of the async transfer

def io_multipart_threaded(operation, dataObj, replica_token, hier_str, session,  fname, nthr = 0, range_for_io = None):
    file_mode = ('r' if operation==Opr.PUT else 'w')
    object_mode = ('w' if operation==Opr.PUT else 'r')
    f = open(fname, file_mode + 'b')
    f.seek(0, os.SEEK_END)
    total_size = dataObj.open('r').seek(0,os.SEEK_END) if operation == Opr.GET else f.tell()
    N = total_size / max(1,abs(nthr)) + 1
    ranges = [six.moves.range(i*N,min(i*N+N,total_size)) for i in range(abs(nthr)) if i*N < total_size]
    bytecounts = []
    parallel_file_mode = ('r' if operation==Opr.PUT else 'r+')
    if nthr > 0:
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers = nthr) as executor:
            for r in ranges:
                File = open( fname, parallel_file_mode + 'b')
                futures.append(executor.submit( io_part, session, dataObj.path, r, File, operation, hier_str, replica_token))
        bytecounts = [ f.result() for f in futures ]
    elif nthr < 0:
        for r in ranges:
            File = open( fname, parallel_file_mode + 'b')
            bytecounts .append( io_part(session, dataObj.path, r, File, operation, hier_str, replica_token) )
    return sum(bytecounts), total_size

# - io_main
#    * get a session object
#    * determine replica information by:
#       - data path
#       - resc (R != '' if specified)

def io_main( d_path, mode , fname, R='', irods_version_hint = (), **kwopt):
    try:
        env_file = os.environ['IRODS_ENVIRONMENT_FILE']
    except KeyError:
        env_file = os.path.expanduser('~/.irods/irods_environment.json')
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None)
    ssl_settings = {'ssl_context': ssl_context}

    with iRODSSession(irods_env_file=env_file, **ssl_settings) as session:

        irods_version = list( irods_version_hint or session.pool._conn.server_version )
        if irods_version < [4,2,8]:
            raise RuntimeError("Need iRODS server version of at least 4.2.8 for parallel transfer")

        if mode.startswith('r') or session.data_objects.exists(d_path):
            pass # - opening data object for read
        else:
            resc_options = {}
            if R: resc_options [kw.RESC_NAME_KW] = R
            if irods_version == [4,2,8]:
                session.data_objects.create(d_path,**resc_options)
            else:
                # Put a file for now ( until 4-2-stable allows good replica from a create-without-write )
                with NamedTemporaryFile() as n:
                    os.system('iput -R "{}" "{}" "{}"'.format(R, n.name, d_path))

        d = session.data_objects.get( d_path )

        Junk = []
        api_return = _data_obj_get_filedesc_info (session.pool._conn, d, mode, target_resc = R, junk = Junk)
        msg = api_return.msg
        Xml = ET.fromstring(msg.replace('\0',''))
        dobj_info = json.loads(Xml.find('buf').text)

        replica_token = dobj_info.get("replica_token")
        resc_hier = dobj_info.get("data_object_info",{}).get("resource_hierarchy")

        if verbose:
            print(json.dumps(dobj_info,indent=4))

        num_thr = int(kwopt.get('n','1'))

        bytes_transferred, bytes_total = \
          io_multipart_threaded ((Opr.PUT,Opr.GET)[mode.startswith('r')],
                                 d, replica_token, resc_hier, session, fname, nthr = num_thr,
                                 range_for_io = None)
        assert bytes_transferred == bytes_total, "thread bytecounts did not sum to total"

if __name__ == '__main__':

    import sys
    opt,arg = getopt.getopt( sys.argv[1:], 'vi:R:n:')

    opts = dict(opt)
    if opts.pop('-v',None) is not None: verbose = True
    irods_vsn = opts.pop('-i',None)

    kwarg = { k.lstrip('-'):v for k,v in opts.items() }

    if irods_vsn is not None:
        kwarg['irods_version_hint'] = ast.literal_eval(irods_vsn)
    
    io_main(*arg,**kwarg)  # argv[1] = data object path
                           # argv[2] = mode: 'r' for GET and 'w' for PUT
                           # argv[3] = file path on local filesystem
##  ________
#   Note - This module requires the concurrent.futures module.
#          On Python2.7, this must be installed using 'pip install futures'.
##  To Test:
# $ dd if=/dev/urandom bs=1k count=150000 of=$HOME/puttest
# $ time python -m irods.parallel -R demoResc -n 3 `ipwd`/test.dat a $HOME/puttest  # PUT to test.dat
# $ time python -m irods.parallel -R demoResc -n 3 `ipwd`/test.dat r $HOME/gettest  # GET from test.dat
# $ diff puttest gettest
