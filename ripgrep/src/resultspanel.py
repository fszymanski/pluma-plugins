# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gtk, Pluma, Gio

from .utils import StatusbarFlashMessage


class ResultsPanel(Gtk.ScrolledWindow, StatusbarFlashMessage):
    __gtype_name__ = "RipgrepResultsPanel"

    def __init__(self, window):
        super().__init__()
        StatusbarFlashMessage.__init__(self)

        self.window_ = window

        store = Gtk.ListStore.new([str, str, str, str, Pluma.Document])
        self.result_view = Gtk.TreeView.new_with_model(store)

        for i, title in enumerate(["Filename", "Line", "Column", "Match"]):
            renderer = Gtk.CellRendererText.new()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_resizable(True)
            self.result_view.append_column(column)

        self.add(self.result_view)

        self.result_view.connect("row-activated", self.goto_match)

        self.show_all()

    def clear(self):
        self.result_view.get_model().clear()

    def get_model(self):
        return self.result_view.get_model()

    def show(self):
        bottom_panel = self.window_.get_bottom_panel()
        bottom_panel.props.visible = True
        bottom_panel.activate_item(self)

    def goto_match(self, result_view, path, _):
        model = result_view.get_model()
        iter_ = model.get_iter(path)

        if (doc := model.get_value(iter_, 4)) is None:
            location = Gio.File.new_for_path(model.get_value(iter_, 0))
            if location.query_exists():
                if (tab := self.window_.get_tab_from_location(location)) is None:
                    self.window_.create_tab_from_uri(location.get_uri(), Pluma.encoding_get_utf8(), 0, False, True)
                else:
                    self.window_.set_active_tab(tab)
            else:
                self.flash_message(self.window_.get_statusbar(), "Cannot open this file")
                return
        else:
            if doc in self.window_.get_documents():
                self.window_.set_active_tab(Pluma.Tab.get_from_document(doc))
            else:
                self.flash_message(self.window_.get_statusbar(), "Cannot jump to this tab")
                return

        line = int(model.get_value(iter_, 1))
        column = int(model.get_value(iter_, 2))
        if (view := self.window_.get_active_view()) is not None:
            buf = view.get_buffer()
            iter_ = buf.get_iter_at_line_offset(line - 1, column - 1)
            buf.place_cursor(iter_)
            view.scroll_to_iter(iter_, 0.25, False, 0, 0)
            view.grab_focus()

# vim: ft=python3
