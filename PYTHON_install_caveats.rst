=======================================================
Python (2.x) and virtualenv for the iRODS administrator
=======================================================

The Python iRODS Client (PRC) can be installed by a
non-administrative user, either as a local install for
the user (using ~/.local) or under a virtual environment.

If the system administrator has installed system packages
for Python and pip, this is generally straightforward. But
note that special care may be needed to install, and upgrade
to, the appropriate versions of the pip and virtualenv modules.
This is especially true on older distributions of the Linux
operating system.

Best practice dictates we ensure we are using the latest
version of pip:

  $ pip install --upgrade --user pip 

Alternatively, pip may be invoked as follows in order to
guarantee we are are referencing (and upgrading) the
right pip module instance for the given Python version:

  $ python${N} -m pip --upgrade --user pip # N is '2' or '3'

(Henceforth in these instructions, note that it is implied
we will specify relevant Python version when there is
a clear preference.)


Local Install
-------------

It is now possible to set up PRC locally for the current user:

  $ python -m pip install --user python_irodsclient


Virtual Environment
-------------------

For this option, we should first install latest version
of the 'virtualenv' module:

  $ python -m pip install --user virtualenv

Then proceed to the creation of the virtual environment and
the installation of the PRC module into that environment:

  $ python -m virtualenv ~/venv
  
  $ source ~/venv/bin/activate
  
  (venv) $ python -m pip install <PyPI_name_or_path>

For that last line, the final argument can be either the
PyPI package name (python-irodsclient) or a directory
in the local filesystem.  In the latter case, the command
is best issued with a path parameter of "." while the
current working directory is a git repository forked from

  http://github.com/irods/python-irodsclient 

