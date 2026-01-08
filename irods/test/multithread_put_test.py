import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import irods.test.helpers
from irods.parallel import abort_parallel_transfers

OBJECT_SIZE = 2 * 1024**3
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

        for signal_name in signal_names:

            #with test_case.subTest(f"Testing with signal {signal_name}"):

            sig = getattr(signal, signal_name)

            session = irods.helpers.make_session()
            hc = irods.helpers.home_collection(session)
            TESTFILE_FILL = b"_" * (1024 * 1024)
            OBJECT_NAME += f"_{irods.helpers.unique_name(time.time())}"
            object_path = f"{hc}/{OBJECT_NAME}"

            with tempfile.NamedTemporaryFile(LOCAL_TEMPFILE_NAME,"wb") as f:           # Create the object to be uploaded.
                for y in range(OBJECT_SIZE // len(TESTFILE_FILL)):
                    f.write(TESTFILE_FILL)

            local_path = None
            # Establish where (ie absolute path) to place the downloaded file, i.e. the  get() target.
            try:
                with tempfile.NamedTemporaryFile(
                    prefix="local_file_issue_722.dat", delete=True
                ) as t:
                    local_path = t.name
        
                # Tell the parent process the name of the local file being "get"ted (got) from iRODS
                print(local_path)
                sys.stdout.flush()
        
                def handler(sig_number,*_):
                    abort_parallel_transfers()
                    exit(128+sig_number)
        
                signal.signal(sig, handler)

                tsession = session.clone()
                data_object_exists = lambda : tsession.data_objects.exists(OBJECT_NAME)
                pid = os.getpid()
                def signal_after_object_exists():
                    while not data_object_exists(): sleep(.1)
                    os.kill(pid, sig)
                threading.Thread(target = signal_after_object_exists).start()

                try:
                    # download the object
                    session.data_objects.put(local_path, object_path)
                except KeyboardInterrupt:
                    abort_parallel_transfers()
                    raise

            finally:
                # Clean up, whether or not the download succeeded.
                if local_path is not None and os.path.exists(local_path):
                    os.unlink(local_path)
                if session.data_objects.exists(object_path):
                    session.data_objects.unlink(object_path, force=True)

            # Assert that transfer threads terminate.
            self.assertTrue(
                wait_until_condition_true(
                   lambda: threading.enumerate() == [threading.current_thread()],
                   10*60.0
                ))
