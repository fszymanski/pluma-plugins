# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import os
import subprocess
from urllib.parse import urlparse

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

# Because of the Markdown syntax skip "(" and ")"
RFC_3986_URI_VALID_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~:/?#[]@!$&'*+,;="


class OpenURIPlugin(GObject.Object, Pluma.ViewActivatable):
    __gtype_name__ = "OpenURIPlugin"

    view = GObject.Property(type=Pluma.View)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        if not hasattr(self.view, "open_uri_handler_id"):
            self.view.open_uri_handler_id = self.view.connect("populate-popup", self.append_open_uri_to_context_menu)

    def do_deactivate(self):
        app = Pluma.App.get_default()
        window = app.get_active_window()
        for view in window.get_views():
            if hasattr(view, "open_uri_handler_id"):
                view.disconnect(view.open_uri_handler_id)
                del view.open_uri_handler_id

    def do_update_state(self):
        pass

    def is_valid_uri(self, uri):
        try:
            result = urlparse(uri)
        except:
            return False

        if all([result.scheme, result.netloc, result.path]) or \
                (all([result.scheme, result.path]) and result.scheme == "file"):
            return True

        return False

    def open_uri(self, uri):
        cmd = ["xdg-open", uri]
        if os.getuid() == 0 and "SUDO_USER" in os.environ:
            cmd = ["sudo", "-u", os.environ["SUDO_USER"]] + cmd

        try:
            subprocess.run(cmd,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except:
            pass

    def append_open_uri_to_context_menu(self, _, popup):
        buf = self.view.get_buffer()
        if buf.get_has_selection():
            start, end = buf.get_selection_bounds()
        else:
            start = buf.get_iter_at_mark(buf.get_insert())
            end = start.copy()

            while start.forward_char():
                if start.get_char() not in RFC_3986_URI_VALID_CHARS:
                    break

            while end.backward_char():
                if end.get_char() not in RFC_3986_URI_VALID_CHARS:
                    end.forward_char()
                    break

        if not (uri := buf.get_text(start, end, False)):
            return

        if self.is_valid_uri(uri):
            menu_item = Gtk.MenuItem.new_with_label(f"Open {uri if len(uri) < 64 else uri[:64] + '...'}")
            menu_item.connect("activate", lambda _: self.open_uri(uri))
            menu_item.show()

            separator = Gtk.SeparatorMenuItem.new()
            separator.show()

            popup.append(separator)
            popup.append(menu_item)

# vim: ft=python3
