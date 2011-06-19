Fabric Platforms
================

Set of classes which can be used to create fabric scripts easy.
These allow you manage multiple machines with different operating
systems with the same commands.


Example
-------

	from fabricplatforms import platform
    from fabric import put
    
	platform.register('myhost.com', 'linux')
	platform.register('mymachost.com', 'darwin')

    # use fabric like normal, setup hosts etc...
    
	def some_task():
		platform.mkdir('/tmp/blah', mode=755, parents=True, use_sudo=False)
		put('/tmp/localfile', '/tmp/blah')