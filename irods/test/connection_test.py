#! /usr/bin/env python
from __future__ import absolute_import
import os
import sys
import time
import unittest
from irods.exception import NetworkException
import irods.test.helpers as helpers


class TestConnections(unittest.TestCase):

    def setUp(self):
        self.sess = helpers.make_session()

    def tearDown(self):
        '''Close connections
        '''
        self.sess.cleanup()

    def test_connection(self):
        with self.sess.pool.get_connection() as conn:
            self.assertTrue(conn)

    
    def test_auto_release_of_old_connection(self):

        do_something = lambda ses: ses.collections.get(helpers.home_collection(ses))

        def get_conn_identity(pool,unittest_obj=None):
            s = (pool.active | pool.idle)
            if unittest_obj:
                unittest_obj.assertEqual (len(s), 1)
            return [conn for conn in s][0]

        with helpers.make_session(refresh_time = 5) as ses:
            do_something(ses)
            c1 = get_conn_identity (ses.pool,self)
            time.sleep(10)
            do_something(ses)
            c2 = get_conn_identity (ses.pool,self)
            self.assertIsNot(c1, c2)


    def test_connection_destructor(self):
        conn = self.sess.pool.get_connection()
        conn.__del__()
        self.assertTrue(conn.socket == None)
        self.assertTrue(conn._disconnected == True)
        conn.release(destroy=True)

    def test_failed_connection(self):
        # mess with the account's port
        saved_port = self.sess.port
        self.sess.pool.account.port = 6666

        # try connecting
        with self.assertRaises(NetworkException):
            self.sess.pool.get_connection()

        # set port back
        self.sess.pool.account.port = saved_port

    def test_send_failure(self):
        with self.sess.pool.get_connection() as conn:
            # try to close connection twice, 2nd one should fail
            conn.disconnect()
            with self.assertRaises(NetworkException):
                conn.disconnect()

    def test_reply_failure(self):
        with self.sess.pool.get_connection() as conn:
            # close connection
            conn.disconnect()

            # try sending reply
            with self.assertRaises(NetworkException):
                conn.reply(0)


if __name__ == '__main__':
    # let the tests find the parent irods lib
    sys.path.insert(0, os.path.abspath('../..'))
    unittest.main()
