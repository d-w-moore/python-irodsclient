=======================================================
Python (2.x) and virtualenv for the iRODS administrator
=======================================================

The Python iRODS Client (PRC) can be installed by a
non-administrative user, either as a local install for
the user (using ~/.local) or under a virtual environment.

If the system administrator has installed system packages
for python and pip, this is not difficult to manage, but
on some older distributions of the Linux operating system
special care is required to arrive at the right results.

Best practice dictates we ensure we are using the latest
version of the pip module (specifying a Python version
via the 'pip2' or 'pip3' commands if necessary):

  $ pip install --upgrade --user pip

Local Install
-------------

It will then be possible to set up PRC locally for the
current user:

  $ python -m pip install --user python_irodsclient

Virtual Environment
-------------------

For this option, we should first install latest version
of the 'virtualenv' module (again, specifying the 
Python version with 'python2' or 'python3' if needed):

  $ python -m pip install --user virtualenv

We proceed to the creation of the virtual environment and
the installation of the PRC module into that environment:

  $ python -m virtualenv ~/venv
  
  $ source ~/venv/bin/activate
  
  (venv) $ python -m pip install <PyPI_name_or_path>

For the last line, the final argument can be either the
PyPI package name (python-irodsclient) or a directory
in the local filesystem.  In the latter case, the command
is best issued with a path parameter of "." while the
current working directory is a git repository forked from

  http://github.com/irods/python-irodsclient 

