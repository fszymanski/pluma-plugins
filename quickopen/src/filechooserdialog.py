# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2023 Filip Szymański <fszymanski.pl@gmail.com>

from enum import IntEnum

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pluma

from .providers import (
    get_files_from_active_document_dir, get_files_from_bookmark_dirs, get_files_from_git_dir,
    get_files_from_open_documents_dir, get_files_from_virtual_root_dir, get_recent_files
)


class COLUMN(IntEnum):
    ICON = 0
    NAME = 1
    LOCATION = 2


@Gtk.Template(resource_path="/org/mate/pluma/plugins/quickopen/ui/filechooserdialog.ui")
class FileChooserDialog(Gtk.Dialog):
    __gtype_name__ = "QuickOpenFileChooserDialog"

    file_label = Gtk.Template.Child()
    file_view = Gtk.Template.Child()
    filter_entry = Gtk.Template.Child()

    def __init__(self, window):
        super().__init__(parent=window)

        self.window_ = window

        column = Gtk.TreeViewColumn.new()

        icon = Gtk.CellRendererPixbuf.new()
        column.pack_start(icon, False)
        column.add_attribute(icon, "gicon", COLUMN.ICON)

        name = Gtk.CellRendererText.new()
        column.pack_start(name, True)
        column.add_attribute(name, "text", COLUMN.NAME)

        self.file_view.append_column(column)

        self.filter_entry.connect("search-changed", lambda _: self.model.refilter())

        selection = self.file_view.get_selection()
        selection.connect("changed", self.file_selection_changed)

#        self.filter_entry.connect("search-changed", self.select_first_row)

        self.file_view.connect("row-activated", self.on_open_button_clicked)

        self.connect("key-press-event", self.on_key_press)

        self.show_all()

        self.model = self.create_and_fill_model(get_recent_files)
        self.file_view.set_model(self.model)

    def create_and_fill_model(self, provider_func):
        self.set_busy_cursor()

        store = Gtk.ListStore.new([Gio.Icon, str, Gio.File])
        for location in provider_func():
            if location.is_native():
                info = location.query_info("standard::*", Gio.FileQueryInfoFlags.NONE, None)
                if info is not None:
                    store.append([info.get_icon(), info.get_display_name(), location])

        sortable = Gtk.TreeModelSort.new_with_model(store)
        sortable.set_sort_func(COLUMN.NAME, self.compare_names, None)
        sortable.set_sort_column_id(COLUMN.NAME, Gtk.SortType.ASCENDING)

        file_filter = sortable.filter_new()
        file_filter.set_visible_func(self.file_filter_func)

        self.set_busy_cursor(False)

        return file_filter

    def set_busy_cursor(self, busy=True):
        if busy:
            self.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        else:
            self.get_window().set_cursor(None)

        Gdk.flush()

    def compare_names(self, model, iter_a, iter_b, _):
        name_a = GLib.utf8_collate_key_for_filename(model.get_value(iter_a, COLUMN.NAME), -1)
        name_b = GLib.utf8_collate_key_for_filename(model.get_value(iter_b, COLUMN.NAME), -1)
        if name_a < name_b:
            return -1
        elif name_a == name_b:
            return 0

        return 1

    def file_filter_func(self, model, iter_, _):
        needle = self.filter_entry.get_text().strip()
        if not needle:
            return True

        haystack = model.get_value(iter_, COLUMN.NAME)
        return GLib.str_match_string(needle, haystack, True)

#    def select_first_row(self, _):
#        selection = self.file_view.get_selection()
#        selection.select_path(Gtk.TreePath.new_first())

    def file_selection_changed(self, selection):
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            location = model.get_value(iter_, COLUMN.LOCATION)
            self.file_label.set_text(location.get_parse_name())
        else:
            self.file_label.set_text("")

    def switch_model(self, provider_func, title):
        self.set_title(f"Quick Open - {title}")

        self.model = self.create_and_fill_model(provider_func)
        self.file_view.set_model(self.model)

    @Gtk.Template.Callback()
    def on_help_button_clicked(self, _):
        Gtk.show_uri(None, "help:pluma-plugins", Gdk.CURRENT_TIME)

    @Gtk.Template.Callback()
    def on_cancel_button_clicked(self, _):
        self.destroy()

    @Gtk.Template.Callback()
    def on_open_button_clicked(self, *_):
        selection = self.file_view.get_selection()
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            location = model.get_value(iter_, COLUMN.LOCATION)
            if location.query_exists():
                if (tab := self.window_.get_tab_from_location(location)) is None:
                    self.window_.create_tab_from_uri(location.get_uri(), Pluma.encoding_get_utf8(), 0, False, True)
                else:
                    self.window_.set_active_tab(tab)

            self.destroy()

    def on_key_press(self, _, event):
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

        if ctrl and event.keyval == Gdk.KEY_r:
            self.switch_model(get_recent_files, "Recent Files")
        elif ctrl and event.keyval == Gdk.KEY_f:
            self.switch_model(get_files_from_virtual_root_dir, "Virtual Root Directory")
        elif ctrl and event.keyval == Gdk.KEY_d:
            self.switch_model(get_files_from_active_document_dir, "Active Document Directory")
        elif ctrl and event.keyval == Gdk.KEY_g:
            self.switch_model(get_files_from_git_dir, "Active Document Git Directory")
        elif ctrl and event.keyval == Gdk.KEY_o:
            self.switch_model(get_files_from_open_documents_dir, "Open Documents Directory")
        elif ctrl and event.keyval == Gdk.KEY_b:
            self.switch_model(get_files_from_bookmark_dirs, "Bookmark Directories")

        return False

# vim: ft=python3
