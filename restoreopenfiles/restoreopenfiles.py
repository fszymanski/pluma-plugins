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

gi.require_version('Peas', '1.0')
gi.require_version('Pluma', '1.0')

from gi.repository import Gio, GLib, GObject, Peas, Pluma

SCHEMA_ID = 'org.mate.pluma.plugins.restoreopenfiles'


class RestoreOpenFilesPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'RestoreOpenFilesPlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        window = self.object
        window.connect('delete-event', self.save_open_files)
        window.connect('show', self.restore_open_files)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass

    def is_only_window(self):
        app = Pluma.App.get_default()
        if len(app.get_windows()) > 1:
            return False

        return True

    def save_open_files(self, window, event):
        uris = []
        for doc in window.get_documents():
            uri = doc.get_uri()
            if uri is not None:
                uris.append(uri)

        settings = Gio.Settings.new(SCHEMA_ID)
        settings.set_value('uris', GLib.Variant('as', uris))

    def restore_open_files(self, window):
        if self.is_only_window():
            settings = Gio.Settings.new(SCHEMA_ID)
            for uri in settings.get_value('uris'):
                if Pluma.utils_uri_exists(uri):
                    Pluma.commands_load_uri(window, uri, None, -1)

# vim: ts=4 et
