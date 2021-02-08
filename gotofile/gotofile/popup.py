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

from enum import IntEnum
import xml.sax.saxutils

import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')

from gi.repository import Gdk, Gio, GLib, Gtk, Pango, Pluma

from .source import *

try:
    import gettext

    gettext.bindtextdomain('pluma-plugins')
    gettext.textdomain('pluma-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s


class Column(IntEnum):
    ICON = 0
    DISPLAY_NAME = 1
    LOCATION = 2


class Popup(Gtk.Window):
    __gtype_name__ = 'Popup'

    def __init__(self, window):
        super().__init__(default_height=360,
                         default_width=500,
                         destroy_with_parent=True,
                         modal=True,
                         title=_('Go To File'),
                         transient_for=window,
                         window_position=Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_entry = Gtk.SearchEntry.new()
        filter_entry.grab_focus_without_selecting()
        filter_entry.set_placeholder_text(_('Search...'))

        model = self.create_and_fill_model(window, filter_entry)

        file_view = Gtk.TreeView.new_with_model(model)
        file_view.set_activate_on_single_click(True)
        file_view.set_enable_search(False)
        file_view.set_headers_visible(False)

        renderer = Gtk.CellRendererPixbuf.new()
        column = Gtk.TreeViewColumn.new()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, 'gicon', Column.ICON)

        renderer = Gtk.CellRendererText.new()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', Column.DISPLAY_NAME)

        file_view.append_column(column)

        selection = file_view.get_selection()

        scroller = Gtk.ScrolledWindow.new(None, None)
        scroller.add(file_view)

        preview_label = Gtk.Label.new(None)
        preview_label.set_halign(Gtk.Align.START)
        preview_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(filter_entry, False, False, 0)
        vbox.pack_start(scroller, True, True, 0)
        vbox.pack_start(preview_label, False, False, 0)
        self.add(vbox)

        self.connect('key-press-event', self.close_on_escape_key)
        filter_entry.connect('search-changed', self.select_first_row, file_view)
        filter_entry.connect('search-changed', self.update_visible_elements, model)
        file_view.connect('row-activated', self.open_file, window)
        selection.connect('changed', self.preview_filename, preview_label)

        self.select_first_row(None, file_view)

    def create_and_fill_model(self, window, filter_entry):
        store = Gtk.ListStore.new([Gio.Icon, str, Gio.File])

        for filename in set(Bookmarks() +
                            DesktopDirectory() +
                            FileBrowserRootDirectory() +
                            HomeDirectory() +
                            OpenDocumentsDirectory(window) +
                            RecentFiles()):
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
        name_a = model.get_value(iter_a, Column.DISPLAY_NAME)
        name_a = GLib.utf8_collate_key_for_filename(name_a, -1)

        name_b = model.get_value(iter_b, Column.DISPLAY_NAME)
        name_b = GLib.utf8_collate_key_for_filename(name_b, -1)
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

    def select_first_row(self, filter_entry, file_view):
        path = Gtk.TreePath.new_first()
        selection = file_view.get_selection()
        selection.select_path(path)

    def close_on_escape_key(self, window, event):
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

# vim: ts=4 et
