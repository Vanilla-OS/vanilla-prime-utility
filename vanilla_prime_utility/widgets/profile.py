# profile.py
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

from gi.repository import Gtk, Gio, GObject, Adw


@Gtk.Template(resource_path='/org/vanillaos/prime-utility/gtk/profile.ui')
class ProfileRow(Adw.ActionRow):
    __gtype_name__ = 'ProfileRow'
    __gsignals__ = {
        'switch': (GObject.SignalFlags.RUN_FIRST, None, (str,str,)),
        'restart': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    img_active = Gtk.Template.Child()
    btn_restart = Gtk.Template.Child()

    def __init__(self, profile, can_transact, latest_switch, current_profile_id, **kwargs):
        super().__init__(**kwargs)

        self.__profile = profile
        self.__can_transact = can_transact
        self.__latest_switch = latest_switch
        self.__current_profile_id = current_profile_id

        self.__build_ui()

    def __build_ui(self):
        self.set_title(self.__profile.get('title'))
        self.set_subtitle(self.__profile.get('description'))
        self.set_activatable(True)
        self.connect("activated", self.__on_activated)

        if not self.__can_transact:
            self.set_activatable(False)
            self.set_tooltip_text(
                _("It is not possible to switch the PRIME profile now. Please restart your device and try again.")
            )
        
        if self.__current_profile_id == self.__profile.get('id'):
            self.img_active.set_visible(True)
            self.btn_restart.set_visible(False)

        if self.__latest_switch == self.__profile.get('id'):
            self.img_active.set_visible(False)
            self.btn_restart.set_visible(True)
            self.btn_restart.connect("clicked", self.__on_restart_clicked)

    def __on_activated(self, widget):
        self.emit('switch', self.__profile.get('id'), self.__profile.get('title'))

    def __on_restart_clicked(self, widget):
        self.emit('restart')
