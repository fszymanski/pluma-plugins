# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gtk, Pluma


class ResultsPanel(Gtk.ScrolledWindow):
    __gtype_name__ = "RipgrepResultsPanel"

    def __init__(self, window):
        super().__init__()

        self.window_ = window

        store = Gtk.ListStore.new([str, str, str, str, Pluma.Document])
        self.result_view = Gtk.TreeView.new_with_model(store)

        for i, title in enumerate(["Filename", "Line", "Column", "Match"]):
            renderer = Gtk.CellRendererText.new()
            column = Gtk.TreeViewColumn(title, renderer, text=i)
            column.set_resizable(True)
            self.result_view.append_column(column)

        self.add(self.result_view)

        self.show_all()

    def clear(self):
        self.result_view.get_model().clear()

    def get_model(self):
        return self.result_view.get_model()

    def show(self):
        bottom_panel = self.window_.get_bottom_panel()
        bottom_panel.props.visible = True
        bottom_panel.activate_item(self)

# vim: ft=python3
