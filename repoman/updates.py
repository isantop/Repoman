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

class Updates(Gtk.Box):

    def __init__(self, parent):
        Gtk.Box.__init__(self, False, 0)

        self.log = logging.getLogger("repoman.Updates")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.log.addHandler(handler)
        self.log.setLevel(logging.WARNING)
        self.log.debug('Loaded repoman.Updates')
        self.repo = Repo()
        self.parent = parent
        self.os_name = self.repo.get_os_name()
        self.handlers = {}
        self.codename = self.repo.get_codename()
        self.system_suites = self.repo.get_system_suites()

        updates_grid = Gtk.Grid()
        updates_grid.set_margin_left(12)
        updates_grid.set_margin_top(24)
        updates_grid.set_margin_right(12)
        updates_grid.set_margin_bottom(12)
        updates_grid.set_hexpand(True)
        updates_grid.set_halign(Gtk.Align.CENTER)
        self.add(updates_grid)

        updates_title = Gtk.Label(_("Update Sources"))
        updates_title.set_halign(Gtk.Align.START)
        Gtk.StyleContext.add_class(updates_title.get_style_context(), "h2")
        updates_grid.attach(updates_title, 0, 0, 1, 1)

        updates_label = Gtk.Label(_("These sources control how %s checks for updates. It is recommended to leave these sources enabled.") % self.os_name)

        updates_label.set_line_wrap(True)
        updates_label.set_halign(Gtk.Align.START)
        updates_grid.attach(updates_label, 0, 1, 1, 1)

        self.checks_grid = Gtk.Grid()
        self.checks_grid.set_margin_left(36)
        self.checks_grid.set_margin_top(24)
        self.checks_grid.set_margin_right(36)
        self.checks_grid.set_margin_bottom(24)
        self.checks_grid.set_column_spacing(12)
        self.checks_grid.set_halign(Gtk.Align.FILL)
        self.checks_grid.set_hexpand(True)
        updates_grid.attach(self.checks_grid, 0, 2, 1, 1)

        self.security_label = Gtk.Label('Important security updates (-security)')
        self.security_label.set_halign(Gtk.Align.START)
        self.updates_label = Gtk.Label(_('Recommended updates (-updates)'))
        self.updates_label.set_halign(Gtk.Align.START)
        self.backports_label = Gtk.Label(_('Unsupported updates (-backports)'))
        self.backports_label.set_halign(Gtk.Align.START)

        self.checks_grid.attach(self.security_label, 0, 0, 1, 1)
        self.checks_grid.attach(self.updates_label, 0, 1, 1, 1)
        self.checks_grid.attach(self.backports_label, 0, 2, 1, 1)

        self.security_switch = Gtk.Switch()
        self.security_switch.set_halign(Gtk.Align.END)
        self.security_switch.set_hexpand(True)
        self.security_switch.suite_name = '-security'
        self.updates_switch = Gtk.Switch()
        self.updates_switch.set_halign(Gtk.Align.END)
        self.updates_switch.suite_name = '-updates'
        self.backports_switch = Gtk.Switch()
        self.backports_switch.set_halign(Gtk.Align.END)
        self.backports_switch.suite_name = '-backports'
        
        self.suite_switches = {
            '-security':  self.security_switch,
            '-updates':   self.updates_switch,
            '-backports': self.backports_switch
        }
        
        self.setup_suites()
        self.security_switch.connect('state-set', self.on_switch_toggled)
        self.updates_switch.connect('state-set', self.on_switch_toggled)
        self.backports_switch.connect('state-set', self.on_switch_toggled)

        self.checks_grid.attach(self.security_switch, 1, 0, 1, 1)
        self.checks_grid.attach(self.updates_switch, 1, 1, 1, 1)
        self.checks_grid.attach(self.backports_switch, 1, 2, 1, 1)

        separator = Gtk.HSeparator()
        updates_grid.attach(separator, 0, 3, 1, 1)

        self.notifications_title = Gtk.Label(_("Update Notifications"))
        self.notifications_title.set_halign(Gtk.Align.START)
        Gtk.StyleContext.add_class(self.notifications_title.get_style_context(), "h2")
        updates_grid.attach(self.notifications_title, 0, 4, 1, 1)

        self.notifications_label = Gtk.Label(_("Change how %s notifies you about pending software updates.") % self.os_name)

        self.notifications_label.set_line_wrap(True)
        self.notifications_label.set_halign(Gtk.Align.CENTER)
        updates_grid.attach(self.notifications_label, 0, 5, 1, 1)

        self.noti_grid = Gtk.Grid()
        self.noti_grid.set_margin_left(12)
        self.noti_grid.set_margin_top(12)
        self.noti_grid.set_margin_right(12)
        self.noti_grid.set_margin_bottom(12)
        updates_grid.attach(self.noti_grid, 0, 6, 1, 1)

        notify_check = Gtk.CheckButton.new_with_label(_("Notify about new updates"))
        self.noti_grid.attach(notify_check, 0, 0, 1, 1)

        auto_check = Gtk.CheckButton.new_with_label(_("Automatically install important security updates."))
        self.noti_grid.attach(auto_check, 0, 1, 1, 1)

        version_check = Gtk.CheckButton.new_with_label(_("Notify about new versions of %s") % self.os_name)
        self.noti_grid.attach(version_check, 0, 2, 1, 1)
    
    def on_switch_toggled(self, widget, data=None):
        """
        Handler for switches.
        """
        if not widget.get_active():
            self.log.debug('Disabling system suite: %s' % widget.suite_name)
            self.repo.remove_suite_from_source(
                source_name='system',
                suite='{}{}'.format(self.codename, widget.suite_name)
            )
        else:
            self.log.debug('Enabling system suite: %s' % widget.suite_name)
            self.repo.add_suite_to_source(
                source_name='system',
                suite='{}{}'.format(self.codename, widget.suite_name)
            )
    
    def setup_suites(self):
        """
        Sets the initial state of the switches in the window.
        """
        for i in self.system_suites:
            suite = i.replace(self.codename, '')
            self.log.debug('Got suite: %s' % suite)
            if suite in self.suite_switches:
                self.suite_switches[suite].set_active(True)
