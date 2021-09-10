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

from pathlib import Path

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import GdkPixbuf, GObject, Gtk, Pluma

import pygit2


class GitBranchIndicatorPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'GitBranchIndicatorPlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            str(Path(self.plugin_info.get_data_dir()) / 'icons' / 'git-branch.svg'),
            *Gtk.IconSize.lookup(Gtk.IconSize.SMALL_TOOLBAR)[1:], True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        self.label = Gtk.Label.new(None)

        self.hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox.pack_start(image, False, False, 0)
        self.hbox.pack_start(self.label, False, False, 0)
        self.hbox.show_all()
        self.hbox.hide()

        self.window.get_statusbar().pack_start(self.hbox, False, False, 48)

        self.window.connect('active-tab-changed', lambda w, t: self.show_git_branch(t))
        self.window.connect('active-tab-state-changed', lambda w: self.show_git_branch(w.get_active_tab()))
        self.window.connect('tab-removed', lambda w, t: self.has_tabs())

    def do_deactivate(self):
        self.hbox.destroy()

    def do_update_state(self):
        pass

    def show_git_branch(self, tab):
        doc = tab.get_document()
        location = doc.get_location()
        if location is not None and location.query_exists():
            repo_path = pygit2.discover_repository(location.get_path())
            if repo_path is not None:
                repo = pygit2.Repository(repo_path)
                self.label.set_text(repo.head.shorthand)

                self.hbox.show()

                return

        self.hbox.hide()

    def has_tabs(self):
        if self.window.get_active_tab() is None:
            self.hbox.hide()

# vim: ts=4 et
