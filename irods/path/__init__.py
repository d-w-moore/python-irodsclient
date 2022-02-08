import re
import logging

_multiple_slash = re.compile('/+')

class iRODSPath(str):
    """A subclass of the Python string that normalizes iRODS logical paths."""

    class LogicalPathError (RuntimeError):
        """An exception indicating an ill-formed or illegal path."""
        pass

    def __new__(cls, *elem_list, **kw):
        """
        Initializes our immutable 'str' object with a normalized form.

        Keywords may include 'absolute'. The default is True, forcing a slash as
        the leading character of the resulting string object.

        Variadic parameters are the path element, strings which may name individual
        collections or sub-hierarchies (internally slash-separated):

        In the resulting object, trailing and redundant path separator are removed,
        as is the "trivial" path element ('.'):

        c = iRODSPath('/tempZone//home',username)
        session.collections.get( c )

        """
        force_absolute = kw.pop('absolute',True)
        if kw:
            logging.warning("iRODSPath options have no effect: %r",kw.items())
        obj = str.__new__(cls,
                          cls.do_path_normalization(elem_list,
                          absolute = force_absolute)  )
        return obj

    @staticmethod
    def resolve_noops_and_updirs(path_components,absolute = True):
        L = list(path_components)
        while '.' in L: L.remove('.')
        initial=[]
        while True:
            try:
                i = L.index('..')
                if i == 0 and absolute:
                    raise iRODSPath.LogicalPathError("No initial '..' permitted")
                if i > 0:
                    del L[i-1:i+1]
                else:
                    initial.append(L.pop(0))
            except ValueError:
                break           # loop until '..' not found in list
        return initial + L


    @staticmethod
    def do_path_normalization(list_of_str, absolute = True):
        s = '/'.join(list_of_str)
        if s[:1] == '/':
            absolute = True
        components = iRODSPath.resolve_noops_and_updirs( _multiple_slash.split(s), absolute)
        path = (
                '/' if absolute else ''
               ) + (
                '/'.join(filter(None, components))
               )
        return path if path else '.'
