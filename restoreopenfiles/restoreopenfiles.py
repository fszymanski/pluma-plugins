# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gdk, Gio, GLib, GObject, Pluma

RESTORE_OPEN_FILES_SCHEMA = "org.mate.pluma.plugins.restoreopenfiles"


class RestoreOpenFilesPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "RestoreOpenFilesPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.handler_ids = [
            self.window.connect("delete-event", lambda *_: self.save_open_files()),
            self.window.connect("key-press-event", self.on_ctrl_q),
            self.window.connect("show", lambda _: self.restore_open_files())
        ]

    def do_deactivate(self):
        for handler_id in self.handler_ids:
            self.window.disconnect(handler_id)

    def do_update_state(self):
        pass

    def is_only_window(self):
        app = Pluma.App.get_default()
        return len(app.get_windows()) <= 1

    def on_ctrl_q(self, _, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)
        if ctrl and event.keyval == Gdk.KEY_q:
            self.save_open_files()

    def save_open_files(self):
        uris = []
        for doc in self.window.get_documents():
            if (uri := doc.get_uri()) is not None and Pluma.utils_uri_exists(uri):
                uris.append(uri)

        settings = Gio.Settings.new(RESTORE_OPEN_FILES_SCHEMA)
        settings.set_value("file-uris", GLib.Variant("as", uris))

        if (doc := self.window.get_active_document()) is not None:
            if (uri := doc.get_uri()) is not None and Pluma.utils_uri_exists(uri):
                settings.set_string("active-document-uri", uri)

    def restore_open_files(self):
        if self.is_only_window():
            settings = Gio.Settings.new(RESTORE_OPEN_FILES_SCHEMA)
            if (uris := settings.get_value("file-uris").unpack()):
                tab = self.window.get_active_tab()
                if tab.get_state() == Pluma.TabState.STATE_LOADING and tab.get_document().get_location() is not None:
                    return

                for uri in uris:
                    location = Gio.file_new_for_uri(uri)
                    if location.query_exists():
                        if self.window.get_tab_from_location(location) is None:
                            self.window.create_tab_from_uri(uri, Pluma.encoding_get_utf8(), 0, False, False)

                if (uri := settings.get_string("active-document-uri")):
                    for doc in self.window.get_documents():
                        if uri == doc.get_uri():
                            self.window.set_active_tab(Pluma.Tab.get_from_document(doc))

                            break

                if len(self.window.get_documents()) > 1 and \
                        tab.get_state() == Pluma.TabState.STATE_NORMAL and \
                        tab.get_document().is_untitled():
                    self.window.close_tab(tab)
