# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

from .pastebindialog import PastebinDialog

MENU_PATH = "/MenuBar/ToolsMenu/ToolsOps_1"


class PastebinPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "PastebinPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def insert_menu(self):
        self.action_group = Gtk.ActionGroup.new("PlumaPastebinPluginActions")
        self.action_group.add_actions([
            ("ToolsUploadToPastebin", None, "Upload to Pastebin...", None, None, lambda _: PastebinDialog(self.window))
        ])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.ui_id = manager.new_merge_id()
        manager.add_ui(self.ui_id,
                       MENU_PATH,
                       "ToolsUploadToPastebinMenu",
                       "ToolsUploadToPastebin",
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
