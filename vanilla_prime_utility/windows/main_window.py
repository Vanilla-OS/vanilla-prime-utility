# main_window.py
#
# Copyright 2024 Mirko Brombin
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
from vanilla_prime_utility.windows.switch_window import PrimeUtilityWindowSwitch


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

    def __build_ui(self, restart=False):
        if not restart:
            self.btn_cancel.connect("clicked", self.__on_cancel_clicked)
        
        for ref in self.__refs:
            GLib.idle_add(ref.get_parent().remove, ref)

        can_transact = PrimeUtilityWrapper.can_transact

        if not PrimeUtilityWrapper.is_supported:
            self.status_no_support.show()
            self.pref_profiles.hide()
            return
            
        if not can_transact:
            self.info_bar.show()
            self.status_no_support.hide()
        
        pw = PrimeUtilityWrapper()
        current_id = pw.get_current()

        for profile in pw.available_profiles():
            row = ProfileRow(profile, can_transact, self.__latest_switch, current_id)
            row.connect("switch", self.__on_switch_profile)
            row.connect("restart", self.__restart)
            self.__refs.append(row)
            self.group_profiles.add(row)
        
    def __set_embedded(self):
        self.btn_cancel.show()
        self.set_deletable(False)

    def __on_cancel_clicked(self, widget):
        self.destroy()

    def __on_switch_profile(self, widget, profile_id, profile_title):
        def handle_response(_widget, response_id):
            if response_id == "ok":
                cmd = PrimeUtilityWrapper().get_set_profile_command(profile_id)
                window = PrimeUtilityWindowSwitch(profile_title, self, cmd, on_close_fn)
                window.connect("restart", self.__restart)
                window.show()

        dialog = Adw.MessageDialog.new(
            self,
            _("Do you want to switch to the '{}' profile?").format(profile_title),
            _("This will require a restart to apply the changes."),
        )
        dialog.add_response("cancel", _("_Cancel"))
        dialog.add_response("ok", _("Switch to '{}'").format(profile_title))
        dialog.set_response_appearance("ok", Adw.ResponseAppearance.SUGGESTED)
        dialog.connect("response", handle_response)
        dialog.present()

        def on_close_fn(res):
            if res:
                self.toast(_("Profile switched to {}!".format(profile_title)))
                self.__write_latest_switch(profile_id)
                self.__build_ui(restart=True)
                return

            self.toast(_("Profile switch failed!"))

    def toast(self, message, timeout=2):
        toast = Adw.Toast.new(message)
        toast.props.timeout = timeout
        self.toasts.add_toast(toast)

    def __restart(self, widget):
        subprocess.run(['gnome-session-quit', '--reboot'])

    @property
    def __latest_switch(self):
        if os.path.exists("/tmp/vanilla_prime_utility.latest"):
            with open("/tmp/vanilla_prime_utility.latest", "r") as f:
                return f.read().strip()

        return 

    def __write_latest_switch(self, profile):
        with open("/tmp/vanilla_prime_utility.latest", "w") as f:
            f.write(profile)

