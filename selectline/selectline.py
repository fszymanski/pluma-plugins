# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

MENU_PATH = "/MenuBar/EditMenu/EditOps_2"


class SelectLinePlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "SelectLinePlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def insert_menu(self):
        self.action_group = Gtk.ActionGroup.new("PlumaSelectLinePluginActions")
        self.action_group.add_actions([
            ("EditSelectLine", None, "Select Line", "<Ctrl>T", None, lambda _: self.select_line())
        ])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.ui_id = manager.new_merge_id()
        manager.add_ui(self.ui_id,
                       MENU_PATH,
                       "EditSelectLineMenu",
                       "EditSelectLine",
                       Gtk.UIManagerItemType.MENUITEM,
                       False)

    def remove_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def do_activate(self):
        self.insert_menu()

    def do_deactivate(self):
        self.remove_menu()

    def do_update_state(self):
        view = self.window.get_active_view()
        self.action_group.set_sensitive(bool(view))

    def select_line(self):
        doc = self.window.get_active_document()
        if doc is None:
            return

        start = doc.get_iter_at_mark(doc.get_insert())
        start.set_line_offset(0)

        end = start.copy()
        if not end.ends_line():
            end.forward_to_line_end()

        doc.select_range(start, end)
