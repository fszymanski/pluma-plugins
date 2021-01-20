# Copyright (C) 2021 Filip Szymański <fszymanski.pl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import GObject, Peas


class RestoreOpenFilesPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'RestoreOpenFilesPlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.window = self.object

        self.window.connect('delete-event', self.write_open_files)
        self.window.connect('show', self.read_open_files)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass

    def write_open_files(self, widget, event):
        pass

    def read_open_files(self, widget):
        pass

# vim: ts=4 et
