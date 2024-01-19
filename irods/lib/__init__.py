"""Hardened and documented versions of commonly functions, some of which may occur elsewhere in the library but have
been found useful enough to be collected into a library.
"""

from ..test.helpers import make_session as _make_session_for_test
from ..data_object import (irods_basename as _irods_basename, 
                           irods_dirname  as _irods_dirname)
from ..path import iRODSPath


def make_session(test_server_version = False , **kwargs):
    """
    test_server_version: Whether to fail when the server is too recent. (False by default)
    kwargs: Keyword arguments, which are all passed on to iRODSSession constructor.
       (Except that 'irods_env_file' which, if present, is intercepted and used to initialize from the named path to an irods environment file.)
    """
    return _make_session_for_test(
            test_server_version = test_server_version,
            **kwargs)


def normalize_path(logical_path):
    """Return the normalized form of the input logical_path.
    """
    return str(iRODSPath(logical_path))


def join_paths(*paths):
    """Concatenate all arguments (interpreted as separate logical path elements) into a normalized logical path.
    """
    return str(iRODSPath(*paths))


def irods_basename(logical_path):
    """Return the last element of the input logical path.  Note this can return the empty string.
    """
    p = normalize_path(logical_path)
    return _irods_basename(p)


def irods_dirname(logical_path):
    """Return the parent path (i.e. the join of all but the last element of) the input logical path.
       This will always have a leading slash ('/').
    """
    p = normalize_path(logical_path)
    res = _irods_dirname(p)
    return res if res != '' else '/'
