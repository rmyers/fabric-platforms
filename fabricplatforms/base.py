from __future__ import with_statement

from collections import defaultdict

import os

from fabric.api import run, sudo, cd, settings, hide

class PlatformError(Exception):
    pass

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

class groupstruct(object):
    """Group helper object for storing groupget results."""
    def __init__(self, name, gid, members=[]):
        self.name = name
        self.gid = gid
        self.members = members

class userstruct(object):
    """User helper object for storing groupget results."""
    def __init__(self, name, uid, gid, group, groups, comment, home, shell):
        self.name = name
        self.uid = uid
        self.gid = gid
        self.group = group
        self.groups = groups
        self.comment = comment
        self.home = home
        self.shell = shell

def shell_escape(text):
    """
    Escape the passed text for use in the shell (Bash).
    The output text will be enclosed in double quotes.
    """
    if not text:
        return '""'
    # We need to escape special characters for bash, and in
    # Python, two backslashes represent one literal backslash.
    # Escape backslashes first, otherwise you would end up escaping the
    # other special characters' escape backslash.
    text = text.replace("\\", "\\\\")
    text = text.replace("$", "\\$")
    text = text.replace("`", "\\`")
    text = text.replace('"', '\\"')
    return '"%s"' % text

class BasePlatform(object):
    """Subclass me to make platform specific changes."""
    
    # filesystem operations
    chgrp_cmd = '/bin/chgrp %s %s %s'
    chmod_cmd = '/bin/chmod %s %s %s'
    chown_cmd = '/bin/chown %s %s%s %s'
    df_cmd = '/bin/df -T'
    digest_cmd = "/usr/bin/sha256sum %s | /bin/gawk '{print $1}'"
    find_cmd = "/usr/bin/find %s -printf '%%p:%%y:%%m:%%u:%%g:%%l:%%s,%%A@,%%T@,%%C@\n'"
    hostname_cmd = '/bin/hostname'
    ln_cmd = '/bin/ln -fs %s %s'
    ls_cmd = '/bin/ls -ARl1 --time-style=+%%s %s'
    mkdir_cmd = '/bin/mkdir %s %s'
    mv_cmd = '/bin/mv %s %s'
    readlink_cmd = '/usr/bin/readlink %s'
    rm_cmd = '/bin/rm %s %s -- %s'
    rmdir_cmd = '/bin/rmdir %s'
    rel_ln_cmd = 'cd %s && /bin/ln -fs %s %s'
    stat_cmd = '/usr/bin/stat -c %%F:%%a:%%U:%%G:%%s,%%X,%%Y,%%Z %s'
    test_cmd = '/usr/bin/test -e %s'
    test_link_cmd = '/usr/bin/test -h %s'
    touch_cmd = '/bin/touch %s'
    untar_cmd = '/bin/tar -x%sf %s -C %s'
    apache_cmd = '/usr/sbin/apache2ctl %s'
    nginx_cmd = '/usr/sbin/nginx %s'
    byte_compile_cmd = '%s -m compileall %s'

    # user and group operations
    groupadd_cmd = '/usr/sbin/groupadd -g %d %s'
    groupdel_cmd = '/usr/sbin/groupdel %s'
    groupget_cmd = '/bin/grep ^%s: /etc/group'
    groupmod_cmd = '/usr/sbin/groupmod -g %d %s'
    groups_cmd = '/bin/cat /etc/group'
    useradd_cmd = '/usr/sbin/useradd -u %d -m %s %s'
    userdel_cmd = '/usr/sbin/userdel -r %s'
    userget_cmd = '/bin/grep ^%s: /etc/passwd'
    userget_groups_cmd = '/usr/bin/id -Gn %s'
    usermod_cmd = '/usr/sbin/usermod %s %s'
    users_cmd = '/bin/cat /etc/passwd'
    
    def execute(self, cmd, use_sudo=False):
        """
        Execute command, either with run or sudo depending on 
        whether the use_sudo kwarg is passed.
        """
        func = sudo if use_sudo else run
        return func(cmd)
    
    def apache(self,  subcommand, use_sudo=False):
        """Executes apachectl command with the passed subcommand."""
        self.execute(self.apache_cmd % (subcommand))

    def nginx(self, subcommand, use_sudo=False):
        self.execute(self.nginx_cmd % subcommand, use_sudo=False)

    def chgrp(self, path, gid, recursive=False, use_sudo=False):
        """Changes the group owner of the specified filesystem path."""

        recursive = ('-R' if recursive else '')
        self.execute(self.chgrp_cmd % (recursive, gid, shell_escape(path)))

    def chmod(self, path, mode, recursive=False, use_sudo=False):
        """Changes the permission mode of the specified filesystem path.
        mode can be an int or symbolic mode representation (e.g. g+rw)
        """

        recursive = ('-R' if recursive else '')
        self.execute(self.chmod_cmd % (recursive, mode, shell_escape(path)))

    def chown(self, path, uid, gid=None, recursive=False, use_sudo=False):
        """Changes the user and possibly the group owner of the specified filesystem path."""

        gid, recursive = (':%s' % gid if gid else ''), ('-R' if recursive else '')
        self.execute(self.chown_cmd % (recursive, uid, gid, shell_escape(path)))

    def hostname(self, use_sudo=False):
        with settings(hide('everything'), warn_only=True):
            hostname = self.execute(self.hostname_cmd)
        return hostname or "Unknown"

    def link(self, target, path, absolute=False, use_sudo=False):
        """Creates the specified symbolic link."""
        
        head, tail = os.path.split(target)
        
        if absolute:
            target = tail
        
        with cd(head):
            self.execute(self.ln_cmd % (target, path), use_sudo=use_sudo)




    def mkdir(self, path, parents=False, use_sudo=False):
        """Creates the specified directory."""
        parents = parents and '-p' or ''
        self.execute(self.mkdir_cmd % (parents, shell_escape(path)), use_sudo=use_sudo)

    def move(self, path, target, use_sudo=False):
        """Moves the specified filesystem path to the specified target."""

        self.execute(self.mv_cmd % (shell_escape(path),
                                    shell_escape(target)), use_sudo=use_sudo)

    def remove(self, path, recursive=False, force=False, link=False, use_sudo=False):
        """Removes the specified filesystem path."""
        # first test if the file is there.
        cmd = self.test_link_cmd if link else self.test_cmd
        with settings(hide('everything'), warn_only=True):
            if self.execute(cmd % shell_escape(path), use_sudo=use_sudo).failed:
                return
        recursive, force = ('-r' if recursive else ''), ('-f' if force else '')
        self.execute(self.rm_cmd % (recursive, force, shell_escape(path)), use_sudo=use_sudo)

    def rmdir(self, path, use_sudo=False):
        """Removes the directory at path."""
        self.execute(self.rmdir_cmd % shell_escape(path), use_sudo=use_sudo)

    def stat(self, path, link=False, use_sudo=False):
        """Generates status information on the specified filesystem path."""
        path = shell_escape(path)
        cmd = self.test_link_cmd if link else self.test_cmd
        # do we even exist?
        with settings(hide('everything'), warn_only=True):
            if self.execute(cmd % path, use_sudo=use_sudo).failed:
                return
        
        with settings(hide('everything'), warn_only=True):
            content = self.execute(self.stat_cmd % path, use_sudo=use_sudo)
        filetype, mode, user, group, values = content.strip().split(':')
        #mode, values = int(mode, 8), [ int(value) for value in values.split(',') ]
        values = [ int(value) for value in values.split(',') ]
        if filetype.lower() == 'directory':
            return dirnode(path, mode, user, group, *values)
        elif filetype.lower() == 'regular file':
            return filenode(path, mode, user, group, *values)
        elif filetype.lower() == 'symbolic link':
            with settings(hide('everything'), warn_only=True):
                target = self.execute(self.readlink_cmd % path, use_sudo=use_sudo)
            return filenode(path, mode, user, group, *values, ftype='link', target=target.strip())
        else:
            return filenode(path, mode, user, group, *values, ftype=filetype)


    def touch(self, path, use_sudo=False):
        """Touches the specified filesystem path."""
        self.execute(self.touch_cmd % shell_escape(path), use_sudo=use_sudo)

    def untar(self, file, path=None, use_sudo=False):
        """Untar a file into path. If Path is None will untar in place."""

        if not path:
            path = os.path.dirname(file)

        file = shell_escape(file)
        path = shell_escape(path)

        if file.endswith('bz2'):
            cmd = self.untar_bz2_cmd % (file, path)
        elif file.endswith('gz'):
            cmd = self.untar_gz_cmd % (file, path)
        else:
            cmd = self.untar_cmd % (file, path)

        self.execute(cmd, use_sudo=use_sudo)

    def byte_compile(self, python_exe, path, use_sudo=False):
        """
        Byte compile all the code in a directory.
        Useful for speeding the initial load times of wsgi apps.
        """
        python_exe = shell_escape(python_exe)
        path = shell_escape(path)
        self.execute(self.byte_compile_cmd % (python_exe, path), use_sudo=use_sudo)
    

    def _attrs_incorrect(self, obj, new_attrs):
        """
        A helper method for testing attrs of a user/group.

        new_attrs should be a dictionary mapping attribute names to values.
        If an attribute's value is None, then checking of that attribute will
        be skipped.

        Return a dictionary of attributes that are not correct and the
        corresponding value the attribute should be changed to.  If all
        attributes are correct, then return an empty dictionary.
        """
        # Attributes that need to have sorted() called on them when comparing.
        needs_sort = set(['groups', 'members'])
        details_incorrect = {}

        for attr, new_value in new_attrs.iteritems():
            if new_value is None:
                continue
            current_value = getattr(obj, attr)
            if attr in needs_sort:
                current_value = sorted(current_value)
                new_value = sorted(new_value)
            if new_value != current_value:
                details_incorrect[attr] = new_value
        return details_incorrect

    #
    # Group methods.
    #

    def groupadd(self, name, gid, members=[], use_sudo=True):
        """Creates the specified system group."""
        self.execute(self.groupadd_cmd % (gid, name), use_sudo=use_sudo)
        for member in members:
            self.usermod(member, groups=[name])

    def groupdel(self, name, use_sudo=True):
        """
        Delete the specified system group.  If the group doesn't exist, then
        do nothing.
        """
        group = self.groupget(name)
        if not group:
            return
        self.execute(self.groupdel_cmd % name, use_sudo=use_sudo)

    def groupget(self, name, use_sudo=True):
        """Gets information on the specified system group."""

        with settings(hide('everything'), warn_only=True):
            content = self.execute(self.groupget_cmd % name)
            if content.failed or not content:
                return None
        name, _, gid, users = content.strip().split(':')
        return groupstruct(name, int(gid), users.split(',') if users else [])

    def groupmod(self, name, gid, use_sudo=True):
        """Modifies the specified system group."""

        self.execute(self.groupmod_cmd % (gid, name))

    def group_incorrect(self, group, name, **new_attrs):
        """Determine which group attributes given are not correct.

        group should be the object returned by a groupget() call.
        name is required.  gid and members are optional and will only be
        checked for out-of-sync'ness if given and not None.

        Return a dictionary of attributes that are not correct and the
        corresponding value the attribute should be changed to.  If all
        attributes are correct, then return an empty dictionary.
        """
        details_incorrect = self._attrs_incorrect(group, new_attrs)
        return details_incorrect

    def groupsync(self, name, gid, members=None, use_sudo=True):
        """Sync the given system group, creating or modifying if needed.

        If members is given, then the group's members will also be checked and
        corrected.  Otherwise if not given, the group's members will not be
        checked or synced.

        Return True if the group needed to be created or modified, and False
        if no action was needed.
        """
        group = self.groupget(name)
        if not group:
            self.groupadd(name, gid, members)
            return True

        details_incorrect = self.group_incorrect(group, name,
                                                 gid=gid, members=members)
        if details_incorrect:
            self.groupmod(name, **details_incorrect)
            return True
        return False

    def groups(self, use_sudo=False):
        """Return a dict of all groups: groupname -> [group_struct, ...]"""
        with settings(hide('everything'), warn_only=True):
            content = self.execute(self.groups_cmd, use_sudo=use_sudo)
            if content.failed:
                raise PlatformError(content)

        groups = {}
        for line in content.splitlines():
            name, _, gid, member_string = line.strip().split(':')
            users = set(member_string.split(',')) if member_string else set()
            group = groupstruct(name, int(gid), users)
            groups[name] = group
        return groups

    #
    # User methods.
    #

    def useradd(self, name, uid, group=None, groups=None, home=None, 
                shell=None, comment=None, use_sudo=True):
        """Creates the specified system user."""

        options = []
        if group:
            options.append('-g %s' % group)
        if groups:
            options.append('-G %s' % ','.join(groups))
        if home:
            options.append('-d %s' % home)
        if shell:
            options.append('-s %s' % shell)
        if comment:
            options.append('-c "%s"' % comment)
        
        cmd = self.useradd_cmd % (uid, ' '.join(options), name)
        
        self.execute(cmd, use_sudo=use_sudo)

    def userdel(self, name, use_sudo=True):
        """
        Delete the specified system user.  If the user doesn't exist, then
        do nothing.
        """
        user = self.userget(name)
        if not user:
            return
        self.execute(self.userdel_cmd % name, use_sudo=use_sudo)

    def userget(self, name, use_sudo=True):
        """Gets information on the specified system user."""

        with settings(hide('everything'), warn_only=True):
            content = self.execute(self.userget_cmd % name, use_sudo=use_sudo)
            if content.failed:
                return None
        name, _, uid, gid, comment, home, shell = content.strip().split(':')
        with settings(hide('everything')):
            content = self.execute(self.userget_groups_cmd % name)
        content = content.strip().split(' ')
        group, groups = content[ 0 ], set(content[ 1: ])
        return userstruct(name, int(uid), int(gid), group, groups, comment, home, shell)

    def usermod(self, name, uid=None, group=None, groups=[], home=None, 
                shell=None, comment=None, use_sudo=True):
        """Modifies the specified system user."""
        
        if self.userget(name) is None:
            return
        
        options = []
        if uid:
            options.append('-u %d' % uid)
        if group:
            options.append('-g %s' % group)
        if home:
            options.append('-d %s -m' % home)
        if shell:
            options.append('-s %s' % shell)
        if comment:
            options.append('-c "%s"' % comment)
        if groups:
            options.append('-aG %s' % ','.join(groups))
        if options:
            self.execute(self.usermod_cmd % (' '.join(options), name))

    def user_incorrect(self, user, name, **new_attrs):
        """Determine which user attributes given are not correct.

        user should be the object returned by a userget() call.
        name is required.  uid, group, groups, home, shell, and comment are all
        optional and will only be checked for out-of-sync'ness if given and not
        None.

        Return a dictionary of attributes that are not correct and the
        corresponding value the attribute should be changed to.  If all
        attributes are correct, then return an empty dictionary.
        """
        details_incorrect = self._attrs_incorrect(user, new_attrs)
        return details_incorrect

    def usersync(self, name, uid=None, group=None, groups=None,
                 home=None, shell=None, comment=None, use_sudo=True):
        """Sync the given system user, creating or modifying if needed.

        name is required.  uid, group, groups, home, shell, and comment are all
        optional and will only be checked for out-of-sync'ness if given.

        Return True if the user needed to be created or modified, and False if
        no action was needed.
        """
        user = self.userget(name, use_sudo=use_sudo)
        if not user:
            self.useradd(name, uid, group, groups, home, shell, comment, use_sudo=use_sudo)
            return True
        details_incorrect = self.user_incorrect(user, name,
                uid=uid, group=group, groups=groups, home=home, shell=shell,
                comment=comment)
        if details_incorrect:
            self.usermod(name, use_sudo=use_sudo, **details_incorrect)
            return True
        return False

    def users(self, min_uid=None, max_uid=None, use_sudo=True):
        """Return a dict of all users: username -> [user_struct, ...]"""
        with settings(hide('everything'), warn_only=True):
            content = self.execute(self.users_cmd, use_sudo=use_sudo)
            if content.failed:
                raise PlatformError(content)

        users = {}
        for line in content.splitlines():
            name, _, uid, gid, comment, home, shell = line.strip().split(':')
            uid = int(uid)
            # Skip over users outside specified min/max uid.
            if min_uid is not None and uid < min_uid:
                continue
            if max_uid is not None and uid > max_uid:
                continue
            with settings(hide('everything'), warn_only=True):
                content = self.execute(self.userget_groups_cmd % name, use_sudo=use_sudo)
                if content.failed:
                    raise PlatformError(content)
            content = content.strip().split(' ')
            group, groups = content[0], set(content[1:])
            user = userstruct(name, uid, int(gid), group, groups, comment, home, shell)
            users[name] = user
        return users
