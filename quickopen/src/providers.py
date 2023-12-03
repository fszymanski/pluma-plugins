# Copyright (C) 2023 Filip Szymański <fszymanski.pl@gmail.com>
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

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk

DIRS_TO_IGNORE = [".git"]
MAX_RECENTS = 200


# Utility functions
def get_files_from_dir(path):
    return [
        Gio.File.new_for_path(str(p))
        for p in Path(path).rglob("*")
        if set(p.parts).isdisjoint(DIRS_TO_IGNORE) and p.is_file()
    ]


def get_file_browser_virtual_root_dir():
    settings = Gio.Settings("org.mate.pluma")
    if "filebrowser" in settings.get_value("active-plugins"):
        settings = Gio.Settings("org.mate.pluma.plugins.filebrowser.on-load")
        uri = settings.get_string("virtual-root")
        return GLib.filename_from_uri(uri)[0]


# Provider functions
def get_recent_files():
    manager = Gtk.RecentManager.get_default()
    items = manager.get_items()
    items.sort(key=lambda i: i.get_visited(), reverse=True)

    count = 0
    for item in items:
        if item.exists() and item.has_group("pluma"):
            yield Gio.File.new_for_uri(item.get_uri())

            count += 1
            if count >= MAX_RECENTS:
                break


def get_files_from_virtual_root_dir():
     if (root_dir := get_file_browser_virtual_root_dir()) is not None:
        return get_files_from_dir(root_dir)

     return []
