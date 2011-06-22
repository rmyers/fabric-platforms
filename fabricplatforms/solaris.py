from base import BasePlatform

class Solaris(BasePlatform):
    
    name = 'sunos'
    # TODO: enforce this or check if < 5.11 works
    release = '5.11'
    
    apache_cmd = '/usr/apache2/2.2/bin/apache2ctl %(subcommand)s'
    untar_cmd = 'cd %(path)s; /bin/tar -xf %(file)s'
    untar_gz_cmd = 'cd %(path)s; /usr/bin/gzcat %(file)s | /usr/bin/tar xf -'
    untar_bz2_cmd = 'cd %(path)s; /usr/bin/bzcat %(file)s | /usr/bin/tar xf -'
    df_cmd = '/bin/df -h'
    # FIXME: Warn that /usr/bin/stat is part of gnu tools need third party tools
    
    # This is gnu find for solaris 5.11 
    find_cmd = "/usr/gnu/bin/find %(file)s -printf '%%p:%%y:%%m:%%u:%%g:%%l:%%s,%%A@,%%T@,%%C@\n'"
    
    groupget_cmd = '/usr/bin/grep ^%(group)s: /etc/group'
    groups_cmd = '/usr/bin/cat /etc/group'
    userget_cmd = '/usr/bin/grep ^%(user)s: /etc/passwd'
    users_cmd = '/usr/bin/cat /etc/passwd'
    # TODO: Check on solaris 5.10 and lower for other problems