#!/usr/bin/python3
'''
   Copyright 2017 Mirko Brombin (brombinmirko@gmail.com)
   Copyright 2017 Ian Santopietro (ian@system76.com)

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

import apt
import dbus
import glob
import logging
import sys
import threading
import time
import queue

import repolib

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, GLib

# Set up threads
GLib.threads_init()

SOURCES_DIR = '/etc/apt/sources.list.d'

bus = dbus.SystemBus()

privileged_object = bus.get_object(
    'ro.santopiet.repoman', '/PPAObject'
)

SYSTEM_SOURCES = [
    '/etc/apt/sources.list.d/system.sources'
]

class AddThread(threading.Thread):
    cache = apt.Cache()

    def __init__(self, parent, source_line):
        threading.Thread.__init__(self)
        self.parent = parent
        self.source_line = source_line
        self.log = logging.getLogger("repoman.PPA.AddThread")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.WARNING)

    def run(self):
        self.log.info("Adding PPA %s" % (self.source_line))
        privileged_object.AddRepo(self.source_line)
        repo = Repo()
        isv_list = repo.get_sources()
        GObject.idle_add(self.parent.parent.stack.list_all.generate_entries, isv_list)
        GObject.idle_add(self.parent.parent.stack.list_all.view.set_sensitive, True)
        GObject.idle_add(self.parent.parent.hbar.spinner.stop)

    def throw_error(self, message):
        GObject.idle_add(self.parent.parent.stack.list_all.throw_error_dialog,
                         message, "error")

class Repo:

    def __init__(self, parent=None):
        self.parent = parent
        self.log = logging.getLogger('repoman.Repo')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)
        self.system_source = repolib.SystemSource()

        self.system_source.load_from_file()
    
    def get_sources(self):
        """
        Gets a list of sources from the disk.
        """
        self.log.debug('Doing list')
        source_obj = repolib.Source()
        sources_dict = {}
        sources = glob.glob('{}/*.sources'.format(SOURCES_DIR))
        for source in sources:
            if not source in SYSTEM_SOURCES:
                source_obj.load_from_file(source)
                sources_dict[source] = source_obj.name
        return sources_dict
    
    def get_source(self, file):
        """
        Returns a repolib.Source object from filename FILE.
        """
        source = repolib.Source()
        source.load_from_file(filename=file)
        return source
        
    def get_system_suites(self):
        """
        Returns a list of suites used by the System Sources.
        """
        system_suites = self.system_source.suites
        return system_suites

    def get_system_comps(self):
        """
        Returns a list of components used by System Sources.
        """
        system_comps = self.system_source.components
        return system_comps
    
    def get_source_code_enabled(self, source_name='system'):
        """
        Returns TRUE if source code is enabled for REPO.
        """

        source_check = repolib.Source(filename='{}.sources'.format(source_name))
        source_check.load_from_file()
        self.log.debug('Found types: %s' % source_check.types)
        for type in source_check.types:
            self.log.debug(type)
            if type.value == "deb-src":
                return True
        
        return False
    
    def get_codename(self):
        """
        Gets the current distro codename.
        """
        return repolib.util.DISTRO_CODENAME
    
    def add_comp_to_source(self, source_name='system', component='main'):
        privileged_object.AddComp(source_name, component)
        return 0
    
    def remove_comp_from_source(self, source_name='system', component='main'):
        privileged_object.DelComp(source_name, component)
        return 0
    
    def add_suite_to_source(self, source_name='system', suite='main'):
        privileged_object.AddSuite(source_name, suite)
        return 0
    
    def remove_suite_from_source(self, source_name='system', suite='main'):
        privileged_object.DelSuite(source_name, suite)
        return 0
    
    def add_source(self, dialog):
        if dialog.ppa_entry.get_text() == '':
            source_name = dialog.name_entry.get_text()
            source_uris = dialog.uri_entry.get_text()
            source_suites = dialog.version_entry.get_text()
            source_components = dialog.component_entry.get_text()
            source_code = dialog.source_check.get_active()
            self.log.debug('Adding full repo...')
            fullrepo = (
                'name={},\n'.format(source_name) +
                'uris={},\n'.format(source_uris) +
                'suites={},\n'.format(source_suites) +
                'components={},\n'.format(source_components) +
                'code={}'.format(source_code)
            )
            self.log.debug('AddFullRepo(%s)' % fullrepo)
            privileged_object.AddFullRepo(
                source_name, source_uris, source_suites, source_components, source_code
            )
        elif dialog.ppa_entry.get_text() != '': 
            source_line = dialog.ppa_entry.get_text()
            self.parent.parent.hbar.spinner.start()
            self.parent.parent.stack.list_all.view.set_sensitive(False)
            t = AddThread(self.parent, source_line)
            t.start()

    def remove_source(self, source):
        privileged_object.DelRepo(source)
    
    def set_source_code_enabled(self, source_name='system', is_enabled=True):
        """
        Enables or disabled source code for the repo.
        """
        privileged_object.SetSource(source_name, is_enabled)
    
    def set_modified_source(self, source):
        print(source.make_source_string())
        
        source_code_enabled = False
        for type in source.types:
            if type.value == "deb-src":
                source_code_enabled = True
        
        source_modified = (
            'name={},\n'.format(source.name) +
            'enabled={},\n'.format(source.enabled.get_bool()) +
            'source={},\n'.format(source_code_enabled) +
            'uris={},\n'.format(' '.join(source.uris)) +
            'suites={},\n'.format(' '.join(source.suites)) +
            'components={},\n'.format(' '.join(source.components)) +
            'filename={}'.format(source.filename) 
        )
        self.log.debug('SetModifiedRepo(%s)' % source_modified)
        
        privileged_object.SetModifiedRepo(
            source.name, source.enabled.get_bool(), source_code_enabled,
            ' '.join(source.uris), ' '.join(source.suites), 
            ' '.join(source.components), source.filename
        )