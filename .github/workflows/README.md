Tests of Python iRODS Client
============================

Test PRC (Python iRODS Client) with an instance of the iRODS server.

[iRODS](https://www.irods.org) is an open source distributed data management system. This is a client API implemented in Python.

The tests we will run are

a.   `main.yml`: static type tests using `mypy`.
b.   `run-the-tests.yml`: set up separate nodes (via Docker compose) to run the client suite.  Nodes include a provider, catalog, and client.
     (See the `docker-testing` subdirectory for the README documentation and implementation of this test mechanism.)
c.   `run-local-suite.yml`: test suite run  within an OS-level virtualized container, also hosting iRODS server and managed by Docker or equivalent.
d.   `run-bats-tests.yml`: run a set of tests, each in its own container under similar conditions to (c).  Each test may have its own unique setup.
     (See the `harness` subdirectory for the README documentation and implementation of this test mechanism.)

Running
-------

The tests are run each time a commit is pushed to this repository or a fork of it.  They are also run when a pull request is made.
