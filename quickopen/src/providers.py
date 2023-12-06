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

import subprocess
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk, Pluma

MAX_RECENTS = 200

#############
# Utilities #
#############

def get_files_from_dir(path):
    settings = Gio.Settings("org.mate.pluma.plugins.quickopen")
    if settings.get_boolean("recursive-file-search"):
        exclude_dirs = [d for d in settings.get_string("exclude-dirs").split(",") if d]
        return [
            Gio.File.new_for_path(str(p))
            for p in Path(path).rglob("*")
            if set(p.parts).isdisjoint(exclude_dirs) and p.is_file()
        ]
    else:
        return [Gio.File.new_for_path(str(p)) for p in Path(path).iterdir() if p.is_file()]


def get_file_browser_virtual_root_dir():
    settings = Gio.Settings("org.mate.pluma")
    if "filebrowser" in settings.get_value("active-plugins"):
        settings = Gio.Settings("org.mate.pluma.plugins.filebrowser.on-load")
        uri = settings.get_string("virtual-root")
        return GLib.filename_from_uri(uri)[0]


def get_open_document_dirs():
    app = Pluma.App.get_default()
    window = app.get_active_window()
    for location in filter(lambda l: l is not None, [d.get_location() for d in window.get_documents() if d.is_local()]):
        if (parent_dir := location.get_parent()) is not None:
            if (path := parent_dir.get_path()) is not None:
                yield path


def get_active_document_dir():
    app = Pluma.App.get_default()
    window = app.get_active_window()
    if (doc := window.get_active_document()) is not None:
        if doc.is_local():
            if (location := doc.get_location()) is not None:
                if (parent_dir := location.get_parent()) is not None:
                    if (path := parent_dir.get_path()) is not None:
                        return path


def get_git_top_level_dir(path):
    proc = subprocess.run("git rev-parse --show-toplevel",
                          stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL,
                          shell=True,
                          cwd=path)
    return proc.stdout.decode("utf-8").strip()


def get_bookmark_dirs():
        path = Path(GLib.get_user_config_dir(), "gtk-3.0/bookmarks")
        if not path.is_file():
            path = Path.home() / ".gtk-bookmarks"

        try:
            with path.open() as bookmarks:
                for bookmark in bookmarks:
                    uri = bookmark.strip().split(" ")[0]
                    if Pluma.utils_uri_has_file_scheme(uri):
                        yield GLib.filename_from_uri(uri)[0]
        except FileNotFoundError:
            pass

#############
# Providers #
#############

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


def get_files_from_open_documents_dir():
    locations = []
    for path in set(get_open_document_dirs()):
        locations += get_files_from_dir(path)

    return locations


def get_files_from_git_dir():
    if (path := get_active_document_dir()) is not None:
        if top_level_dir := get_git_top_level_dir(path):
            return get_files_from_dir(top_level_dir)

    return []


def get_files_from_bookmark_dirs():
    locations = []
    for path in get_bookmark_dirs():
        locations += get_files_from_dir(path)

    return locations
