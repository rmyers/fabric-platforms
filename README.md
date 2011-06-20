Fabric Platforms
================
Set of classes which can be used to create fabric scripts easy.
These allow you manage multiple machines with different operating
systems with the same commands.

Status
------
Currently only the Linux and SunOS platform class are available. 
Darwin is in the works. FreeBSD and NetBSD should be simple 
and may just work with the linux platform. The sample fabfile.py
has a few examples on how to use it. Otherwise poke around in
the source BasePlatform class.

Example
-------
A little lite on documentation at the moment. But take a peek at 
the sample fabfile.py

	from fabric.api import env
	
	from fabricplatforms import platform
	
	env.hosts = ['localhost']
	
	# platform will try and get the correct os class but you
	# can do this or override the default like:
	# platform.register_platform('dotted.path.to.platform')
	# platform.register('localhost', 'myplatform')
	
	def create_dir():
	    platform.mkdir('/tmp/blah')
	    platform.move('/tmp/blah', '/tmp/blah2')
	    directory = platform.stat('/tmp/blah2')
	    print "Permissions on Directory: ", directory.mode
	    print "atime on Directory: ", directory.atime
	    platform.chmod('/tmp/blah2', 600)
	    directory = platform.stat('/tmp/blah2')
	    print "Permissions on Directory: ", directory.mode
	    print "atime on Directory: ", directory.atime
	    platform.rmdir('/tmp/blah2')
	    print "Platform hostname: ", platform.hostname()
	
	def create_dummy_user():
	    "Create and remove a dummy user, be careful 'userdel' works!"
	    
	    # Find the highest uid in the system and add 1000 to it
	    # skip uid's above 60000 since 'nobody' lives at the end of
	    # of the range.
	    users = platform.users(max_uid=60000)
	    max_uid = 0
	    for _, user_obj in users.iteritems():
	        if user_obj.uid > max_uid:
	            max_uid = user_obj.uid
	    
	    print "Found max uid: ", max_uid
	    platform.useradd('asdfghjk', max_uid + 1000, shell='/bin/bash')
	    asdf = platform.userget('asdfghjk')
	    print "Dummy user created, %s %s" % (asdf.name, asdf.uid)
	    platform.userdel('asdfghjk')

Installing fabric on Solaris
----------------------------
Just some notes about getting fabric to build on Solaris. (or pycrypto that is)

1. First install the following packages on Solaris 11
   - gmp
   - system/library/math/header-math
   - setuptools-26
2. Run `sudo easy_install pip` or `sudo easy_install virtualenv`
3. Create virtualenv or just run pip install like:

		CFLAGS=-I/usr/include/gmp pip install fabric

Enjoy fabric!