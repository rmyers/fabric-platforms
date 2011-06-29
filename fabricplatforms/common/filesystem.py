import os

class dirnode(object):
    """Directory helper object for storing results from stat and find commands."""

    def __init__(self, path, mode = None, user = None, group = None, size = None,
        atime = None, mtime = None, ctime = None):
        """Constructor."""

        self.atime = atime
        self.container = '%s/' % os.path.dirname(path.rstrip('/'))
        self.ctime = ctime
        self.dirs = {}
        self.files = {}
        self.group = group
        self.mode = mode
        self.mtime = mtime
        self.name = '%s/' % os.path.basename(path.rstrip('/'))
        self.path = '%s/' % path.rstrip('/')
        self.size = size
        self.ftype = 'directory'
        self.user = user

    def __getattr__(self, name):
        """Acquires the specified attribute."""
        try:
            return self.files[ name ]
        except KeyError:
            try:
                return self.dirs[ name ]
            except KeyError:
                raise AttributeError("'dirnode' object has no attribute '%s'" % name)

class filenode(object):
    """File helper object for storing results from stat and find commands."""

    def __init__(self, path, mode=None, user=None, group=None, size=None, 
                 atime=None, mtime=None, ctime=None, **parameters):
        self.atime = atime
        self.ctime = ctime
        self.container = '%s/' % os.path.dirname(path)
        self.digest = parameters.get('digest', None)
        self.group = group
        self.mode = mode
        self.mtime = mtime
        self.name = os.path.basename(path)
        self.path = path
        self.size = size
        self.target = parameters.get('target', None)
        self.ftype = parameters.get('ftype', 'file')
        self.user = user