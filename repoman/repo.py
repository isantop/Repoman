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
import logging
import sys
import threading
import queue
import time

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
    
    def set_source_code_enabled(self, source_name='system', is_enabled=True):
        """
        Enables or disabled source code for the repo.
        """
        privileged_object.SetSource(source_name, is_enabled)
    
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