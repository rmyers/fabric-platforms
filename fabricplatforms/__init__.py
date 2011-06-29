import logging

from fabric.state import env
from fabric.api import run, settings, hide

from linux import Linux
from solaris import Solaris
from darwin import Darwin
from base import PlatformError

def import_object(dotted_path):
    """
    Import an object from a dotted path string.

    If dotted_path contains no dots, then try to import and return a module.
    """
    parts = dotted_path.rsplit('.', 1)
    mod = __import__(parts[0])
    mod_only = len(parts) == 1
    if mod_only:
        return mod
    obj = getattr(mod, parts[1])
    return obj

class Platform(object):
    """
    Base platform.
    
    Handles registration of platforms and hosts. Serves as a proxy
    to the underlining os specific classes. 
    """
    
    def __init__(self):
        self.PLATFORMS = {}
        self.HOSTS = {}
    
    def register_platform(self, platform):
        if isinstance(platform, basestring):
            platform = import_object(platform)
        
        name = getattr(platform, 'name', platform.__name__.lower())
        self.PLATFORMS[name] = platform()
    
    def register(self, host, platform_name):
        if platform_name not in self.PLATFORMS.iterkeys():
            logging.error('Available platforms: %s', [x for x in self.PLATFORMS.iterkeys()])
            raise PlatformError("Platform not registered")
        platform = self.PLATFORMS[platform_name]
        self.HOSTS[host] = platform
    
    def get_platform_for_host(self, host):
        try:
            platform = self.HOSTS[host]
        except KeyError:
            # Try to discover the host platform type:
            with settings(hide('everything'), warn_only=True):
                output = run('uname -sr')
                if output.failed:
                    raise PlatformError("Could not determine host type, please register it!")
                uname, release = str(output).strip().lower().split()
                logging.info("Searching for Platform: %s (%s)" % (uname, release))
                try:
                    platform = self.PLATFORMS[uname]
                    self.register(host, uname)
                except KeyError:
                    raise PlatformError("Platform for %s not registered" % uname)
        return platform
        
        
    def __getattr__(self, name):
        """Proxies method calls on this connector to the underlying system."""
        try:
            return super(Platform, self).__getattr__(name)
        except AttributeError:
            platform = self.get_platform_for_host(env['host'])
            return getattr(platform, name)
           
platform = Platform()

# Register some default platform classes
platform.register_platform(Linux)
platform.register_platform(Solaris)
platform.register_platform(Darwin)