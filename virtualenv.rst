===================
Virtualenv problems
===================

Python2 virtual environments seem broken for Ubuntu 16,
although the Python iRODS Client (PRC) package can still be
installed in the system global python environment or in
the user environment.

As an example, a non-root user such as the irods Unix user
can use the following commands to install the PRC "locally",
meaning that the ~/.local directory will be used as the
install prefix:

  pip install --upgrade pip
  pip install --user /path/to/python-irodsclient


