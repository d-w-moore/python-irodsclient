import os
import re
from signal import setitimer, SIGALRM, signal, SIG_DFL, ITIMER_REAL, SIGUSR1
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import irods.test.helpers
from irods.parallel import abort_parallel_transfers

OBJECT_SIZE = 2 * 1024**3
TESTFILE_FILL = b"_" * (1024 * 1024)
OBJECT_NAME = "data_put_issue__722"
LOCAL_TEMPFILE_NAME = "data_object_to_put_issue_722.dat"

def wait_until_condition_true(func, interval, sleep=.1):
    t0 = time.time()
    while ((t:=time.time()) - t0) < interval:
        if (value:=func()): break
        time.sleep(sleep)
    return value

class Test(unittest.TestCase):

    def test_put__issue_722(self):
      signal_names=("SIGTERM", "SIGINT")

      with tempfile.NamedTemporaryFile(mode="wb") as f:           # Create the object to be uploaded.
         for y in range(OBJECT_SIZE // len(TESTFILE_FILL)):
             f.write(TESTFILE_FILL)
             local_path = f.name

         def _abort_them(*_):
             print ("aborted1")
             abort_parallel_transfers()
             print ("aborted2")

         if True:
            #with test_case.subTest(f"Testing with signal {signal_name}"):
#           signal(SIGALRM,
#                   _abort_them)
            signal(SIGUSR1,
                    _abort_them)

            session = irods.helpers.make_session()
            hc = irods.helpers.home_collection(session)
            object_path = f"{hc}/put_target_issue_722_{irods.test.helpers.unique_name(time.time())}"

            # Establish where (ie absolute path) to place the downloaded file, i.e. the  get() target.
            try:
        
                # Tell the parent process the name of the local file being "get"ted (got) from iRODS
        
                tsession = session.clone()
                data_object_exists = lambda:tsession.data_objects.exists(object_path)
                pid=os.getpid()
                def signal_after_object_exists():
                    while not data_object_exists():
                      print('*',flush=True,end='')
                      time.sleep(.1)
                    #setitimer(ITIMER_REAL,0.01)
                    print("killsent")
                    os.kill(pid,SIGUSR1)
                    #abort_parallel_transfers()
                    #session.cleanup()

                threading.Thread(target = signal_after_object_exists).start()
                session. data_objects. put(local_path, object_path)

                # Assert that transfer threads terminate.
                self.assertTrue(
                    wait_until_condition_true(
                       lambda: threading.enumerate() == [threading.current_thread()],
                       10*60.0))
            finally:
                # Clean up, whether or not the download succeeded.
                pass
#               if session.data_objects.exists(object_path):
#                   session.data_objects.unlink(object_path, force=True)
#               ))               
