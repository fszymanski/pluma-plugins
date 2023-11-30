from enum import IntEnum

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gio, Gdk, GLib, Gtk, Pluma

from .providers import get_recent_files


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
    cancel_button = Gtk.Template.Child()
    help_button = Gtk.Template.Child()
    open_button = Gtk.Template.Child()

    def __init__(self, window):
        super().__init__(parent=window)

        self._window = window

        column = Gtk.TreeViewColumn()

        icon = Gtk.CellRendererPixbuf()
        column.pack_start(icon, False)
        column.add_attribute(icon, "gicon", COLUMN.ICON)

        name = Gtk.CellRendererText()
        column.pack_start(name, True)
        column.add_attribute(name, "text", COLUMN.NAME)

        self.file_view.append_column(column)

        model = self.create_and_fill_model(get_recent_files)
        self.file_view.set_model(model)

        self.filter_entry.connect("search-changed", lambda _: model.refilter())

        selection = self.file_view.get_selection()
        selection.connect("changed", self.file_selection_changed)

        self.filter_entry.connect("search-changed", self.select_first_row)

        self.file_view.connect("row-activated", self.open_file)

        self.open_button.connect("clicked", self.open_file)
        self.cancel_button.connect("clicked", lambda _: self.destroy())

        self.connect("key-press-event", self.on_key_press)

        self.show_all()

    def create_and_fill_model(self, provider_func):
        store = Gtk.ListStore(Gio.Icon, str, Gio.File)

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

        return file_filter

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

    def select_first_row(self, _):
        selection = self.file_view.get_selection()
        selection.select_path(Gtk.TreePath.new_first())

    def file_selection_changed(self, selection):
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            location = model.get_value(iter_, COLUMN.LOCATION)
            self.file_label.set_text(location.get_parse_name())
        else:
            self.file_label.set_text("")

    def open_file(self, *_):
        selection = self.file_view.get_selection()
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            location = model.get_value(iter_, COLUMN.LOCATION)
            if location.query_exists():
                if (tab := self._window.get_tab_from_location(location)) is None:
                    self._window.create_tab_from_uri(location.get_uri(), Pluma.encoding_get_utf8(), 0, False, True)
                else:
                    self._window.set_active_tab(tab)

            self.destroy()

    def on_key_press(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

        return False
