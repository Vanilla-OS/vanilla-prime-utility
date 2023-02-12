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
    __gtype_name__ = 'DriverRow'
    __gsignals__ = {
        'switch': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, profile, can_transact, **kwargs):
        super().__init__(**kwargs)

        self.__profile = profile

        self.__build_ui()

    def __build_ui(self):
        self.set_title(self.__profile.get('title'))
        self.set_subtitle(self.__profile.get('description'))
        self.set_activatable(True)
        self.connect("activated", self.__on_activated)

    def __on_activated(self, widget):
        self.emit('switch', self.__profile)
