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

import xml.sax.saxutils
from enum import IntEnum
from gettext import gettext as _

import gi

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import Gdk, Gio, GLib, Gtk, Pango, Pluma

from .providers import *


class Column(IntEnum):
    ICON = 0
    DISPLAY_NAME = 1
    LOCATION = 2


class Popup(Gtk.Window):
    __gtype_name__ = 'GoToFilePopup'

    def __init__(self, window):
        super().__init__(default_height=360,
                         default_width=500,
                         destroy_with_parent=True,
                         modal=True,
                         transient_for=window,
                         window_position=Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_entry = Gtk.SearchEntry.new()
        filter_entry.grab_focus_without_selecting()
        filter_entry.set_placeholder_text(_('Search...'))

        model = self.create_and_fill_model(window, filter_entry)

        renderer = Gtk.CellRendererPixbuf.new()
        column = Gtk.TreeViewColumn.new()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'gicon', Column.ICON)

        renderer = Gtk.CellRendererText.new()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', Column.DISPLAY_NAME)

        file_view = Gtk.TreeView.new_with_model(model)
        file_view.set_activate_on_single_click(True)
        file_view.set_enable_search(False)
        file_view.set_headers_visible(False)
        file_view.append_column(column)
        file_view.connect('row-activated', self.open_file, window)

        filter_entry.connect('search-changed', self.select_first_row, file_view)
        filter_entry.connect('search-changed', self.update_visible_elements, model)

        scroller = Gtk.ScrolledWindow.new(None, None)
        scroller.add(file_view)

        preview_label = Gtk.Label.new(None)
        preview_label.set_halign(Gtk.Align.START)
        preview_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        selection = file_view.get_selection()
        selection.connect('changed', self.preview_filename, preview_label)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(filter_entry, False, False, 0)
        vbox.pack_start(scroller, True, True, 0)
        vbox.pack_start(preview_label, False, False, 0)
        self.add(vbox)

        self.connect('key-press-event', self.destroy_on_escape_key)

        self.total_rows = len(model)
        self.set_title(_('Go To File ({0}/{0})').format(self.total_rows))

        self.select_first_row(None, file_view)

    def create_and_fill_model(self, window, filter_entry):
        store = Gtk.ListStore.new([Gio.Icon, str, Gio.File])

        settings = Gio.Settings.new('org.mate.pluma.plugins.gotofile')
        for filename in set(BookmarksProvider(settings) +
                            DesktopDirectoryProvider(settings) +
                            FileBrowserRootDirectoryProvider(settings) +
                            HomeDirectoryProvider(settings) +
                            OpenDocumentsDirectoryProvider(settings, window) +
                            RecentFilesProvider(settings)):
            location = Gio.file_new_for_path(filename)
            if location.is_native():
                info = location.query_info('standard::*', Gio.FileQueryInfoFlags.NONE, None)
                if info is not None:
                    store.append([info.get_icon(), info.get_display_name(), location])

        sortable = Gtk.TreeModelSort.new_with_model(store)
        sortable.set_sort_func(Column.DISPLAY_NAME, self.compare_display_name, None)
        sortable.set_sort_column_id(Column.DISPLAY_NAME, Gtk.SortType.ASCENDING)

        filter_ = sortable.filter_new()
        filter_.set_visible_func(self.file_visible, filter_entry)

        return filter_

    def compare_display_name(self, model, iter_a, iter_b, user_data):
        name_a = GLib.utf8_collate_key_for_filename(model.get_value(iter_a, Column.DISPLAY_NAME), -1)
        name_b = GLib.utf8_collate_key_for_filename(model.get_value(iter_b, Column.DISPLAY_NAME), -1)
        if name_a < name_b:
            return -1
        elif name_a == name_b:
            return 0

        return 1

    def file_visible(self, model, iter_, filter_entry):
        needle = filter_entry.get_text().strip()
        if not needle:
            return True

        haystack = model.get_value(iter_, Column.DISPLAY_NAME)
        return GLib.str_match_string(needle, haystack, True)

    def update_visible_elements(self, filter_entry, model):
        model.refilter()

        filtered_rows = len(model)
        self.set_title(_('Go To File ({0}/{1})').format(self.total_rows, filtered_rows))

    def select_first_row(self, filter_entry, file_view):
        path = Gtk.TreePath.new_first()
        selection = file_view.get_selection()
        selection.select_path(path)

    def destroy_on_escape_key(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

        return False

    def preview_filename(self, selection, preview_label):
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            location = model.get_value(iter_, Column.LOCATION)
            filename = xml.sax.saxutils.escape(location.get_path())

            preview_label.set_markup(filename)

    def open_file(self, file_view, path, column, window):
        model = file_view.get_model()
        try:
            iter_ = model.get_iter(path)
        except ValueError:
            pass
        else:
            location = model.get_value(iter_, Column.LOCATION)
            Pluma.commands_load_uri(window, location.get_uri(), None, -1)

            self.destroy()

# vim: ft=python3 ts=4 et
