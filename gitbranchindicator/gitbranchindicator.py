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

import os
from pathlib import Path

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import GdkPixbuf, GObject, Gtk, Pango, Pluma

from utils import get_current_git_branch, is_git_dir


class GitBranchIndicatorPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'GitBranchIndicatorPlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            os.fspath(Path(self.plugin_info.get_data_dir(), 'icons/git-branch.svg')),
            *Gtk.IconSize.lookup(Gtk.IconSize.SMALL_TOOLBAR)[1:], True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        self.label = Gtk.Label.new(None)
        self.label.set_max_width_chars(32)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)

        self.hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox.pack_start(image, False, False, 0)
        self.hbox.pack_start(self.label, True, True, 0)
        self.hbox.show_all()
        self.hbox.hide()

        self.window.get_statusbar().pack_start(self.hbox, False, False, 48)

        self.handlers = [
            self.window.connect('active-tab-changed', lambda w, t: self.show_git_branch(t)),
            self.window.connect('active-tab-state-changed', lambda w: self.show_git_branch(w.get_active_tab())),
            self.window.connect('tab-removed', lambda w, t: self.hide_if_no_tabs())
        ]

    def do_deactivate(self):
        for handler in self.handlers:
            self.window.disconnect(handler)

        self.hbox.destroy()

    def do_update_state(self):
        pass

    def show_git_branch(self, tab):
        doc = tab.get_document()
        location = doc.get_location()
        if location is not None and location.query_exists():
            path = Path(location.get_path()).parent
            if is_git_dir(path):
                self.label.set_text(get_current_git_branch(path))

                self.hbox.show()

                return

        self.hbox.hide()

    def hide_if_no_tabs(self):
        if self.window.get_active_tab() is None:
            self.hbox.hide()

# vim: ft=python3 ts=4 et
