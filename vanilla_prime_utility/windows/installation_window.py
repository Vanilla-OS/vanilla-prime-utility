# installation_window.py
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
# SPDX-License-Identifier: GPL-3.0-only

from gi.repository import Gtk, GObject, Gio, Gdk, GLib, Adw, Vte, Pango


@Gtk.Template(resource_path='/org/vanillaos/prime-utility/gtk/window-installation.ui')
class PrimeUtilityWindowInstallation(Adw.Window):
    __gtype_name__ = 'PrimeUtilityWindowInstallation'
    __gsignals__ = {
        'restart': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    status_install = Gtk.Template.Child()
    status_done = Gtk.Template.Child()
    console_output = Gtk.Template.Child()
    btn_restart = Gtk.Template.Child()

    def __init__(self, title, window, command, on_close_fn, **kwargs):
        super().__init__(**kwargs)
        self.set_transient_for(window)
        self.status_install.set_title(_("Installing '{}'…").format(title))
        self.__window = window
        self.__command = command
        self.__status = 0
        self.__on_close_fn = on_close_fn
        self.__terminal = Vte.Terminal()
        self.__font = Pango.FontDescription()
        self.__font.set_family("Ubuntu Mono")
        self.__font.set_size(13 * Pango.SCALE)
        self.__font.set_weight(Pango.Weight.NORMAL)
        self.__font.set_stretch(Pango.Stretch.NORMAL)

        self.__build_ui()

    def __build_ui(self):
        self.__terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.ON)
        self.__terminal.set_font(self.__font)
        self.__terminal.set_mouse_autohide(True)

        self.console_output.append(self.__terminal)

        self.__terminal.connect("child-exited", self.on_vte_child_exited)
        self.connect("close-request", self.on_close)
        self.btn_restart.connect("clicked", self.on_btn_restart_clicked)

        palette = ["#353535", "#c01c28", "#26a269", "#a2734c", "#12488b", "#a347ba", "#2aa1b3", "#cfcfcf", "#5d5d5d", "#f66151", "#33d17a", "#e9ad0c", "#2a7bde", "#c061cb", "#33c7de", "#ffffff"]
        
        FOREGROUND = palette[0]
        BACKGROUND = palette[15]
        FOREGROUND_DARK = palette[15]
        BACKGROUND_DARK = palette[0]
        
        self.fg = Gdk.RGBA()
        self.bg = Gdk.RGBA()

        self.colors = [Gdk.RGBA() for c in palette]
        [color.parse(s) for (color, s) in zip(self.colors, palette)]
        desktop_schema = Gio.Settings.new('org.gnome.desktop.interface')
        if desktop_schema.get_enum('color-scheme') == 0:
            self.fg.parse(FOREGROUND)
            self.bg.parse(BACKGROUND)
        elif desktop_schema.get_enum('color-scheme') == 1:
            self.fg.parse(FOREGROUND_DARK)
            self.bg.parse(BACKGROUND_DARK)
        self.__terminal.set_colors(self.fg, self.bg, self.colors)

        self.__terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            None,
            ["/bin/sh", "-c", self.__command],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None,
            -1,
            None,
            None,
            None,
        )

    def __pulse(self):
        self.progressbar.pulse()
        GObject.timeout_add(100, self.__pulse)

    def on_vte_child_exited(self, terminal, status, *args):
        status = not bool(status)
        self.__status = status

        if status:
            self.status_install.hide()
            self.status_done.show()
        else:
            self.set_title(_("Installation Failed"))
            self.status_install.set_title(_("Installation Failed"))
            self.status_install.set_description(_("The installation of the driver failed. Please try again later."))

        self.set_deletable(True)

    def on_close(self, *args):
        if self.__on_close_fn:
            self.__on_close_fn(self.__status)

        self.destroy()

    def on_btn_restart_clicked(self, *args):
        self.emit("restart")
        self.destroy()
    