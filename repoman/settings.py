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

import logging

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from .repo import Repo

import gettext
gettext.bindtextdomain('repoman', '/usr/share/repoman/po')
gettext.textdomain("repoman")
_ = gettext.gettext

class Settings(Gtk.Box):

    def __init__(self, parent):
        Gtk.Box.__init__(self, False, 0)

        # self.ppa = PPA(self)
        # self.os_name = self.ppa.get_os_name()
        self.os_name = "TESTING"
        self.handlers = {}
        self.repo = Repo()
        self.parent = parent
        self.log = logging.getLogger('repoman.Settings')
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.DEBUG)
        self.log.debug('Loaded settings!')

        self.system_comps = self.repo.get_system_comps()
        self.system_source_code = self.repo.get_source_code_enabled(
            source_name='system'
        )
        self.log.debug('System source code enabled: %s' % self.system_source_code)
        self.codename = self.repo.get_codename()
        self.proposed_updates = False
        if '{}-proposed'.format(self.codename) in self.repo.get_system_suites():
            self.proposed_updates = True

        settings_grid = Gtk.Grid()
        settings_grid.set_margin_left(12)
        settings_grid.set_margin_top(24)
        settings_grid.set_margin_right(12)
        settings_grid.set_margin_bottom(12)
        settings_grid.set_hexpand(True)
        settings_grid.set_halign(Gtk.Align.CENTER)
        self.add(settings_grid)

        sources_title = Gtk.Label(_("Official Sources"))
        sources_title.set_halign(Gtk.Align.START)
        Gtk.StyleContext.add_class(sources_title.get_style_context(), "h2")
        settings_grid.attach(sources_title, 0, 0, 1, 1)

        sources_label = Gtk.Label(_("Official sources are those provided by %s and its developers. It's recommended to leave these sources enabled.") % self.os_name)
        sources_label.set_line_wrap(True)
        sources_label.set_halign(Gtk.Align.START)
        settings_grid.attach(sources_label, 0, 1, 1, 1)

        self.checks_grid = Gtk.Grid()
        self.checks_grid.set_margin_left(36)
        self.checks_grid.set_margin_top(24)
        self.checks_grid.set_margin_right(36)
        self.checks_grid.set_margin_bottom(24)
        self.checks_grid.set_column_spacing(12)
        self.checks_grid.set_halign(Gtk.Align.FILL)
        self.checks_grid.set_hexpand(True)
        settings_grid.attach(self.checks_grid, 0, 2, 1, 1)

        self.main_label = Gtk.Label('Officially supported software (main)')
        self.main_label.set_halign(Gtk.Align.START)
        self.universe_label = Gtk.Label(_('Community-maintained software (universe)'))
        self.universe_label.set_halign(Gtk.Align.START)
        self.restricted_label = Gtk.Label(_('Proprietary drivers for devices (restricted)'))
        self.restricted_label.set_halign(Gtk.Align.START)
        self.multiverse_label = Gtk.Label(_('Software with Copyright or legal restrictions (multiverse)'))
        self.multiverse_label.set_halign(Gtk.Align.START)
        self.checks_grid.attach(self.main_label, 0, 0, 1, 1)
        self.checks_grid.attach(self.universe_label, 0, 1, 1, 1)
        self.checks_grid.attach(self.restricted_label, 0, 2, 1, 1)
        self.checks_grid.attach(self.multiverse_label, 0, 3, 1, 1)

        self.main_switch = Gtk.Switch()
        self.main_switch.set_halign(Gtk.Align.END)
        self.main_switch.set_hexpand(True)
        self.main_switch.component_name = 'main'
        
        self.universe_switch = Gtk.Switch()
        self.universe_switch.set_halign(Gtk.Align.END)
        self.universe_switch.component_name = 'universe'
        
        self.restricted_switch = Gtk.Switch()
        self.restricted_switch.set_halign(Gtk.Align.END)
        self.restricted_switch.component_name = 'restricted'
        
        self.multiverse_switch = Gtk.Switch()
        self.multiverse_switch.set_halign(Gtk.Align.END)
        self.multiverse_switch.component_name = 'multiverse'
        
        self.component_switches = {
            'main':       self.main_switch,
            'universe':   self.universe_switch,
            'restricted': self.restricted_switch,
            'multiverse': self.multiverse_switch
        }
        self.setup_comps()

        self.main_switch.connect('state-set', self.on_switch_toggled)
        self.universe_switch.connect('state-set', self.on_switch_toggled)
        self.restricted_switch.connect('state-set', self.on_switch_toggled)
        self.multiverse_switch.connect('state-set', self.on_switch_toggled)


        self.checks_grid.attach(self.main_switch, 1, 0, 1, 1)
        self.checks_grid.attach(self.universe_switch, 1, 1, 1, 1)
        self.checks_grid.attach(self.restricted_switch, 1, 2, 1, 1)
        self.checks_grid.attach(self.multiverse_switch, 1, 3, 1, 1)

        developer_options = Gtk.Expander()
        developer_options.set_label(_("Developer Options (Advanced)"))
        settings_grid.attach(developer_options, 0, 3, 1, 1)

        self.developer_box = Gtk.VBox()
        self.developer_box.set_margin_left(36)
        self.developer_box.set_margin_top(12)
        self.developer_box.set_margin_right(36)
        self.developer_box.set_margin_bottom(12)

        self.developer_grid = Gtk.Grid()
        self.developer_grid.set_column_spacing(12)
        self.developer_grid.set_halign(Gtk.Align.FILL)

        developer_label = Gtk.Label(_("These options are those which are primarily of interest to developers."))
        developer_label.set_halign(Gtk.Align.START)
        developer_label.set_line_wrap(True)
        developer_label.set_margin_bottom(12)
        self.developer_box.add(developer_label)
        self.developer_box.add(self.developer_grid)

        self.source_check = Gtk.CheckButton(label=_('Include Source Code'))
        self.source_check.set_halign(Gtk.Align.START)
        self.source_check.set_active(self.system_source_code)
        self.source_check.connect('toggled', self.on_source_toggled)
        proposed_label = Gtk.Label(_('Unstable Updates (proposed)'))
        proposed_label.set_halign(Gtk.Align.START)
        proposed_label.set_hexpand(True)
        self.proposed_switch = Gtk.Switch()
        self.proposed_switch.set_halign(Gtk.Align.END)
        self.proposed_switch.set_active(self.proposed_updates)
        self.proposed_switch.connect('state-set', self.on_proposed_toggled)
        self.proposed_switch.set_hexpand(True)


        developer_options.add(self.developer_box)

        self.developer_grid.attach(self.source_check, 0, 1, 2, 1)
        self.developer_grid.attach(proposed_label, 0, 2, 1, 1)
        self.developer_grid.attach(self.proposed_switch, 1, 2, 1, 1)
        
        self.show_all()
    
    def on_source_toggled(self, widget):
        """Handler for source-code check."""
        self.repo.set_source_code_enabled(
            source_name='system',
            is_enabled=widget.get_active()
        )
    
    def on_proposed_toggled(self, widget, data=None):
        """ Handler for proposed switch. """
        if not widget.get_active():
            self.log.debug('Disabling Proposed')
            self.repo.remove_suite_from_source(
                source_name='system',
                suite='{}-proposed'.format(self.codename)
            )
        else:
            self.log.debug('Enabling Proposed')
            self.repo.add_suite_to_source(
                source_name='system',
                suite='{}-proposed'.format(self.codename)
            )
    
    def on_switch_toggled(self, widget, data=None):
        """
        Handler for switches.
        """
        if not widget.get_active():
            self.log.debug('Disabling system component: %s' % widget.component_name)
            self.repo.remove_comp_from_source(
                source_name='system',
                component=widget.component_name
            )
        else:
            self.log.debug('Enabling system component: %s' % widget.component_name)
            self.repo.add_comp_to_source(
                source_name='system',
                component=widget.component_name
            )

    def setup_comps(self):
        """
        Sets the initial state of the switches in the window.
        """
        
        for i in self.system_comps:
            self.log.debug('Got component: %s' % i)
            if i in self.component_switches:
                self.component_switches[i].set_active(True)
    