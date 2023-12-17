# Copyright (C) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>
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

# TODO: Once opened, go to the most recently active document (tab)

import gi

gi.require_version("Pluma", "1.0")
from gi.repository import Gio, GLib, GObject, Pluma

RESTORE_OPEN_FILES_SCHEMA = "org.mate.pluma.plugins.restoreopenfiles"


class RestoreOpenFilesPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "RestoreOpenFilesPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.handlers = [
            self.window.connect("delete-event", lambda *_: self.save_open_files()),
            self.window.connect("show", lambda _: self.restore_open_files())
        ]

    def do_deactivate(self):
        for handler in self.handlers:
            self.window.disconnect(handler)

    def do_update_state(self):
        pass

    def is_only_window(self):
        app = Pluma.App.get_default()

        return len(app.get_windows()) <= 1

    def save_open_files(self):
        uris = []
        for doc in self.window.get_documents():
            uri = doc.get_uri()
            if uri is not None:
                uris.append(uri)

        settings = Gio.Settings(RESTORE_OPEN_FILES_SCHEMA)
        settings.set_value("uris", GLib.Variant("as", uris))

    def restore_open_files(self):
        if self.is_only_window():
            settings = Gio.Settings(RESTORE_OPEN_FILES_SCHEMA)
            uris = settings.get_value("uris").unpack()
            if len(uris):
                tab = self.window.get_active_tab()
                if tab.get_state() == Pluma.TabState.STATE_NORMAL and tab.get_document().get_uri() is None:
                    self.window.close_tab(tab)

            for uri in uris:
                location = Gio.file_new_for_uri(uri)
                if location.query_exists():
                    if self.window.get_tab_from_location(location) is None:
                        self.window.create_tab_from_uri(location.get_uri(), Pluma.encoding_get_utf8(), 0, False, False)
