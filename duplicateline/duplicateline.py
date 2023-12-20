# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

MENU_PATH = "/MenuBar/EditMenu/EditOps_1"


class DuplicateLinePlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "DuplicateLinePlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def insert_menu(self):
        self.action_group = Gtk.ActionGroup.new("PlumaDuplicateLinePluginActions")
        self.action_group.add_actions([
            ("EditDuplicateLineSelection", None, "Duplicate Line/Selection", "<Ctrl><Shift>D", None, lambda _: self.duplicate_line())
        ])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.ui_id = manager.new_merge_id()
        manager.add_ui(self.ui_id,
                       MENU_PATH,
                       "EditDuplicateLineSelectionMenu",
                       "EditDuplicateLineSelection",
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
        self.action_group.set_sensitive(bool(view) and view.get_editable())

    def duplicate_line(self):
        if (doc := self.window.get_active_document()) is None:
            return

        if doc.get_has_selection():
            start, end = doc.get_selection_bounds()
            if start.get_line() != end.get_line():
                start.set_line_offset(0)
                if not end.ends_line():
                    end.forward_to_line_end()

                lines = doc.get_text(start, end, False)
                if lines[-1] != "\n":
                    lines = f"\n{lines}"

                doc.insert(end, lines)
            else:
                selection = doc.get_text(start, end, False)

                doc.move_mark_by_name("selection_bound", start)
                doc.insert(end, selection)
        else:
            start = doc.get_iter_at_mark(doc.get_insert())
            start.set_line_offset(0)

            end = start.copy()
            if not end.ends_line():
                end.forward_to_line_end()

            curr_line = doc.get_text(start, end, False)
            doc.insert(end, f"\n{curr_line}")
