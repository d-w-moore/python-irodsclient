#! /usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import
import os
import sys
import unittest
import json
from irods.models import Collection, DataObject
import irods.test.helpers as helpers

class TestWithSSL(unittest.TestCase):

    def test_ssl_with_server_verify_set_to_none_281(self):
        env_file = os.path.expanduser('~/.irods/irods_environment.json')
        with helpers.file_backed_up(env_file):
            env = json.load(open(env_file))
            env.update({ "irods_client_server_negotiation": "request_server_negotiation",
                         "irods_client_server_policy": "CS_NEG_REQUIRE",
                         "irods_ssl_ca_certificate_file": "/path/to/some/file.crt",  # does not need to exist
                         "irods_ssl_verify_server": "none",
                         "irods_encryption_key_size": 32,
                         "irods_encryption_salt_size": 8,
                         "irods_encryption_num_hash_rounds": 16,
                         "irods_encryption_algorithm": "AES-256-CBC" })
            with open(env_file,'w') as f:
                json.dump(env,f)
            with helpers.make_session() as session:
                c = session.collections.get('/{session.zone}/home/{session.username}'.format(**locals()))


class TestContinueQuery(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # once only (before all tests), set up large collection
        print ("Creating a large collection...", file = sys.stderr)
        with helpers.make_session() as sess:
            # Create test collection
            cls.coll_path = '/{}/home/{}/test_dir'.format(sess.zone, sess.username)
            cls.obj_count = 2500
            cls.coll = helpers.make_test_collection( sess, cls.coll_path, cls.obj_count)

    def setUp(self):
        # open the session (per-test)
        self.sess = helpers.make_session()

    def tearDown(self):
        # close the session (per-test)
        self.sess.cleanup()

    @classmethod
    def tearDownClass(cls):
        """Remove test data."""
        # once only (after all tests), delete large collection
        print ("Deleting the large collection...", file = sys.stderr)
        with helpers.make_session() as sess:
            sess.collections.remove(cls.coll_path, recurse=True, force=True)

    def test_walk_large_collection(self):
        for current_coll, subcolls, objects in self.coll.walk():
            # check number of objects
            self.assertEqual(len(objects), self.obj_count)

            # check object names
            counter = 0
            for obj in objects:
                self.assertEqual(
                    obj.name, "test" + str(counter).zfill(6) + ".txt")
                counter += 1

    def test_files_generator(self):
        # Query for all files in test collection
        query = self.sess.query(DataObject.name, Collection.name).filter(
            Collection.name == self.coll_path)

        counter = 0

        for result in query:
            # what we should see
            object_path = self.coll_path + \
                "/test" + str(counter).zfill(6) + ".txt"

            # what we see
            result_path = "{}/{}".format(
                result[Collection.name], result[DataObject.name])

            # compare
            self.assertEqual(result_path, object_path)
            counter += 1

        # make sure we got all of them
        self.assertEqual(counter, self.obj_count)

    def test_query_offset_limit_all(self):
        # settings
        max_rows = 100
        offset = 50

        # Query should close after getting max_rows
        results = self.sess.query(DataObject.name, Collection.name).offset(
            offset).limit(max_rows).all()
        self.assertEqual(len(results), max_rows)


if __name__ == '__main__':
    # let the tests find the parent irods lib
    sys.path.insert(0, os.path.abspath('../..'))
    unittest.main()
