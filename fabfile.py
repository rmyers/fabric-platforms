from fabric.api import env

from fabricplatforms import platform

env.hosts = ['localhost']

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