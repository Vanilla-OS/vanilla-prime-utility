# main_window.py
#
# Copyright 2023 Mirko Brombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import subprocess
from gi.repository import Gtk, GLib, Gdk, Adw

from vanilla_prime_utility.utils.run_async import RunAsync
from vanilla_prime_utility.utils.wrapper import PrimeUtilityWrapper
from vanilla_prime_utility.widgets.profile import ProfileRow
from vanilla_prime_utility.windows.installation_window import PrimeUtilityWindowInstallation


@Gtk.Template(resource_path='/org/vanillaos/prime-utility/gtk/window-main.ui')
class PrimeUtilityWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'PrimeUtilityWindow'
    btn_cancel = Gtk.Template.Child()
    toasts = Gtk.Template.Child()
    info_bar = Gtk.Template.Child()
    info_bar_label = Gtk.Template.Child()
    pref_profiles = Gtk.Template.Child()
    group_profiles = Gtk.Template.Child()
    status_no_support = Gtk.Template.Child()

    def __init__(self, embedded, **kwargs):
        super().__init__(**kwargs)

        self.__refs = []

        self.__build_ui()
        if embedded:
            self.__set_embedded()

    def __build_ui(self):
        self.btn_cancel.connect("clicked", self.__on_cancel_clicked)
        can_transact = PrimeUtilityWrapper.can_transact

        if not PrimeUtilityWrapper.is_supported:
            self.status_no_support.show()
            self.pref_profiles.hide()
        elif not can_transact:
            self.info_bar.show()
            self.status_no_support.hide()
        
        for profile in PrimeUtilityWrapper.available_profiles():
            row = ProfileRow(profile, can_transact)
            row.connect("switch", self.__on_switch_profile)
            self.group_profiles.add(row)
        
    def __set_embedded(self):
        self.btn_cancel.show()
        self.set_deletable(False)

    def __on_cancel_clicked(self, widget):
        self.destroy()

    def __on_switch_profile(self, widget, profile):
        print(profile)

    def toast(self, message, timeout=2):
        toast = Adw.Toast.new(message)
        toast.props.timeout = timeout
        self.toasts.add_toast(toast)

    def __restart(self, widget):
        subprocess.run(['gnome-session-quit', '--reboot'])
