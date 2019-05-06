#!/usr/bin/python3
'''
   Copyright 2019 Ian Santopietro (ian@system76.com)

   This file is part of Repoman.

    Repoman is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Repoman is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Repoman.  If not, see <http://www.gnu.org/licenses/>.
'''
import gi
from gi.repository import GObject
import dbus
import dbus.service
import dbus.mainloop.glib

import time

import repolib

class RepomanException(dbus.DBusException):
    _dbus_error_name = 'ro.santopiet.repoman.RepomanException'

class PermissionDeniedByPolicy(dbus.DBusException):
    _dbus_error_name = 'ro.santopiet.repoman.PermissionDeniedByPolicy'

class AptException(Exception):
    pass

class PPAObject(dbus.service.Object):

    def __init__(self, conn=None, object_path=None, bus_name=None):
        dbus.service.Object.__init__(self, conn, object_path, bus_name)

        # The following variables are used bu _check_polkit_privilege
        self.dbus_info = None
        self.polkit = None
        self.enforce_polkit = True
        # self.sp = SoftwareProperties()
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='s', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def DelRepo(self, ppa, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        # PPA Remove code here
        try:
            return 0
        except:
            raise AptException("Could not remove the APT Source")
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='ss', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def AddComp(self, repo, comp, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        
        try:
            source = repolib.Source()
            source.load_from_file(filename='{}.sources'.format(repo))
            if not comp in source.components:
                source.components.append(comp)
            source.components.sort()
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not add %s to source %s" % (comp, repo))
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='ss', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def DelComp(self, repo, comp, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        
        try:
            source = repolib.Source()
            source.load_from_file(filename='{}.sources'.format(repo))
            if comp in source.components:
                source.components.remove(comp)
            source.components.sort()
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not add %s to source %s" % (comp, repo))
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='ss', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def AddSuite(self, repo, suite, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        
        try:
            source = repolib.Source()
            source.load_from_file(filename='{}.sources'.format(repo))
            if not suite in source.suites:
                source.suites.append(suite)
            source.suites.sort()
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not add %s to source %s" % (comp, repo))
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='ss', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def DelSuite(self, repo, suite, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        
        try:
            source = repolib.Source()
            source.load_from_file(filename='{}.sources'.format(repo))
            if suite in source.suites:
                source.suites.remove(suite)
            source.suites.sort()
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not add %s to source %s" % (comp, repo))
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='sb', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def SetSource(self, repo, state, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        
        try:
            source = repolib.Source()
            source.load_from_file(filename='{}.sources'.format(repo))
            source.set_source_enabled(state)
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not add %s to source %s" % (comp, repo))
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='s', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def AddRepo(self, ppa, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        # PPA Add code here
        try:
            return 0
        except:
            raise AptException("Could not remove the APT Source")
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='sbbssss', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def SetModifiedRepo(
        self, 
        name, 
        enabled, 
        source_code, 
        uris, 
        suites, 
        components, 
        filename,
        sender=None, 
        conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        # PPA Modify code here
        try:
            source = repolib.Source(filename=filename)
            source.load_from_file()
            source.name=name
            source.set_enabled(enabled)
            source.uris=uris.split()
            source.suites=suites.split()
            source.components=components.split()
            source.set_source_enabled(source_code)
            source.save_to_disk()
            return 0
        except:
            raise AptException("Could not modify the APT Source")
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='sb', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def SetCompEnabled(self, comp_name, is_enabled, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        # PPA Modify code here
        return 0

    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='sb', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def SetChildEnabled(self, child_name, is_enabled, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        # PPA Modify code here
        return 0
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='b', out_signature='i',
        sender_keyword='sender', connection_keyword='conn'
    )
    def SetSourceCodeEnabled(self, is_enabled, sender=None, conn=None):
        self._check_polkit_privilege(
            sender, conn, 'ro.santopiet.repoman.modppa'
        )
        return 0

    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='', out_signature='',
        sender_keyword='sender', connection_keyword='conn'
    )
    def RaiseException(self, sender=None, conn=None):
        raise RepomanException('Error managing software sources!')
    
    @dbus.service.method(
        "ro.santopiet.repoman.Interface",
        in_signature='', out_signature='',
        sender_keyword='sender', connection_keyword='conn'
    )
    def Exit(self, sender=None, conn=None):
        mainloop.quit()
    
    @classmethod
    def _log_in_file(klass, filename, string):
        date = time.asctime(time.localtime())
        ff = open(filename, "a")
        ff.write("%s : %s\n" %(date,str(string)))
        ff.close()
    
    @classmethod
    def _strip_source_line(self, source):
        source = source.replace("#", "# ")
        source = source.replace("[", "")
        source = source.replace("]", "")
        source = source.replace("'", "")
        source = source.replace("  ", " ")
        return source

    def _check_polkit_privilege(self, sender, conn, privilege):
        # from jockey
        '''Verify that sender has a given PolicyKit privilege.

        sender is the sender's (private) D-BUS name, such as ":1:42"
        (sender_keyword in @dbus.service.methods). conn is
        the dbus.Connection object (connection_keyword in
        @dbus.service.methods). privilege is the PolicyKit privilege string.

        This method returns if the caller is privileged, and otherwise throws a
        PermissionDeniedByPolicy exception.
        '''
        if sender is None and conn is None:
            # called locally, not through D-BUS
            return
        if not self.enforce_polkit:
            # that happens for testing purposes when running on the session
            # bus, and it does not make sense to restrict operations here
            return

        # get peer PID
        if self.dbus_info is None:
            self.dbus_info = dbus.Interface(conn.get_object('org.freedesktop.DBus',
                '/org/freedesktop/DBus/Bus', False), 'org.freedesktop.DBus')
        pid = self.dbus_info.GetConnectionUnixProcessID(sender)
        
        # query PolicyKit
        if self.polkit is None:
            self.polkit = dbus.Interface(dbus.SystemBus().get_object(
                'org.freedesktop.PolicyKit1',
                '/org/freedesktop/PolicyKit1/Authority', False),
                'org.freedesktop.PolicyKit1.Authority')
        try:
            # we don't need is_challenge return here, since we call with AllowUserInteraction
            (is_auth, _, details) = self.polkit.CheckAuthorization(
                    ('unix-process', {'pid': dbus.UInt32(pid, variant_level=1),
                    'start-time': dbus.UInt64(0, variant_level=1)}), 
                    privilege, {'': ''}, dbus.UInt32(1), '', timeout=600)
        except dbus.DBusException as e:
            if e._dbus_error_name == 'org.freedesktop.DBus.Error.ServiceUnknown':
                # polkitd timed out, connect again
                self.polkit = None
                return self._check_polkit_privilege(sender, conn, privilege)
            else:
                raise

        if not is_auth:
            PPAObject._log_in_file('/tmp/repoman.log','_check_polkit_privilege: sender %s on connection %s pid %i is not authorized for %s: %s' %
                    (sender, conn, pid, privilege, str(details)))
            raise PermissionDeniedByPolicy(privilege)


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    bus = dbus.SystemBus()
    name = dbus.service.BusName("ro.santopiet.repoman", bus)
    object = PPAObject(bus, '/PPAObject')

    mainloop = GObject.MainLoop()
    mainloop.run()