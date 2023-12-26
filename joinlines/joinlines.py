# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

MENU_PATH = "/MenuBar/EditMenu/EditOps_1"


class JoinLinesPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "JoinLinesPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def insert_menu(self):
        self.action_group = Gtk.ActionGroup.new("PlumaJoinLinesPluginActions")
        self.action_group.add_actions([
            ("EditJoinLines", None, "Join Lines", "<Ctrl>J", None, lambda _: self.join_lines())
        ])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.ui_id = manager.new_merge_id()
        manager.add_ui(self.ui_id,
                       MENU_PATH,
                       "EditJoinLinesMenu",
                       "EditJoinLines",
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
        self.action_group.set_sensitive(self.window.get_active_document() is not None)

    def join_lines(self):
        doc = self.window.get_active_document()
        if doc is None:
            return

        if doc.get_has_selection():
            start, end = doc.get_selection_bounds()
        else:
            start = doc.get_iter_at_mark(doc.get_insert())

            end = start.copy()
            end.forward_line()

        doc.join_lines(start, end)
