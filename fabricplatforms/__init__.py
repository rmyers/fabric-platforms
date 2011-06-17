
class PlatformError(Exception):
	pass

class Platform(object):
	"""Base platform. Handles registration of platforms and hosts."""
	
	def __init__(self):
		self.PLATFORMS = {}
		self.HOSTS = {}
	
	def register_platform(self, name, platform):
		self.PLATFORMS[name] = platform
	
	def register(self, host, platform_name):
		if platform_name not in self.PLATFORMS.iterkeys():
			raise PlatformError("Platform not registered")
		platform = self.PLATFORMS[platform_name]
		self.HOSTS[host] = platform
	
platform = Platform()