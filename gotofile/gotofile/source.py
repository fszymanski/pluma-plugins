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

__all__ = [
    'Bookmarks', 'DesktopDirectory', 'FileBrowserRootDirectory',
    'HomeDirectory', 'OpenDocumentsDirectory', 'RecentFiles'
]

import os
from pathlib import Path

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')

from gi.repository import Gio, GLib, Gtk, Pluma

def get_files_from_dir(path):
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    yield entry.path
    except (FileNotFoundError, NotADirectoryError):
        pass


class Bookmarks(list):
    def __init__(self):
        self.fill()

    def get_bookmark_dirs(self):
        filename = Path(GLib.get_user_config_dir()) / 'gtk-3.0' / 'bookmarks'
        if not filename.is_file():
            filename = Path.home() / '.gtk-bookmarks'

        try:
            with filename.open() as bookmarks:
                for bookmark in bookmarks:
                    uri = bookmark.strip().split(' ')[0]
                    if Pluma.utils_uri_has_file_scheme(uri):
                        yield GLib.filename_from_uri(uri)[0]
        except FileNotFoundError:
            pass

    def fill(self):
        bookmark_dirs = self.get_bookmark_dirs()
        if bookmark_dirs is not None:
            for dirname in bookmark_dirs:
                for filename in get_files_from_dir(dirname):
                    self.append(filename)


class DesktopDirectory(list):
    def __init__(self):
        self.fill()

    def fill(self):
        desktop_dir = GLib.get_user_special_dir(GLib.USER_DIRECTORY_DESKTOP)
        if desktop_dir is not None:
            for filename in get_files_from_dir(desktop_dir):
                self.append(filename)


class FileBrowserRootDirectory(list):
    def __init__(self):
        self.fill()

    def get_file_browser_root_dir_uri(self):
        settings = Gio.Settings.new('org.mate.pluma')
        if 'filebrowser' in settings.get_value('active-plugins'):
            settings = Gio.Settings.new('org.mate.pluma.plugins.filebrowser.on-load')
            return settings.get_string('virtual-root')

    def fill(self):
        uri = self.get_file_browser_root_dir_uri()
        if uri is not None:
            for filename in get_files_from_dir(GLib.filename_from_uri(uri)[0]):
                self.append(filename)


class HomeDirectory(list):
    def __init__(self):
        self.fill()

    def fill(self):
        for filename in get_files_from_dir(Path.home()):
            self.append(filename)


class OpenDocumentsDirectory(list):
    def __init__(self, window):
        self.window = window

        self.fill()

    def get_open_document_dirs(self):
        locations = filter(lambda l: l is not None, [d.get_location() for d in self.window.get_documents()])
        for location in locations:
            parent_dir = location.get_parent()
            if parent_dir is not None:
                dirname = parent_dir.get_path()
                if dirname is not None:
                    yield dirname

    def fill(self):
        for dirname in set(self.get_open_document_dirs()):
            for filename in get_files_from_dir(dirname):
                self.append(filename)


class RecentFiles(list):
    def __init__(self, max_recents=200):
        self.max_recents = max_recents

        self.fill()

    def fill(self):
        manager = Gtk.RecentManager.get_default()
        items = manager.get_items()
        items.sort(key=lambda i: i.get_visited(), reverse=True)

        count = 0
        for item in items:
            if item.has_group('pluma'):
                uri = item.get_uri()
                if Pluma.utils_uri_exists(uri):
                    self.append(GLib.filename_from_uri(uri)[0])

                    count += 1
                    if count >= self.max_recents:
                        break

# vim: ts=4 et
