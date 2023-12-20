# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GObject, Gtk, Pluma

UI_STR = """
<ui>
    <menubar name='MenuBar'>
        <menu name='ToolsMenu' action='Tools'>
            <placeholder name='ToolsOps_2'>
                <menu name='ToolsMacroMenu' action='ToolsMacro'>
                    <menuitem name='MacroStartRecordingMenu' action='MacroStartRecording'/>
                    <menuitem name='MacroStopRecordingMenu' action='MacroStopRecording'/>
                    <menuitem name='MacroPlaybackMenu' action='MacroPlayback'/>
                </menu>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class MacroPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "MacroPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def insert_menu(self):
        self.action_group = Gtk.ActionGroup.new("PlumaMacroPluginActions")
        self.action_group.add_actions([
            ("ToolsMacro", None, "Macro", None, None, None),
            ("MacroStartRecording", Gtk.STOCK_MEDIA_RECORD, "Start Recording", None, None, lambda _: self.start_recording_macro()),
            ("MacroStopRecording", Gtk.STOCK_MEDIA_STOP, "Stop Recording", None, None, lambda _: self.stop_recording_macro()),
            ("MacroPlayback", Gtk.STOCK_MEDIA_PLAY, "Playback", "<Ctrl><Alt>M", None, lambda _: self.playback_macro())
        ])

        self.set_action_sensitivity([True, False, False])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.ui_id = manager.add_ui_from_string(UI_STR)

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
        pass

    def start_recording_macro(self):
        self.macro = []

        self.set_action_sensitivity([False, True, False])

        self.handler_id = self.window.connect("key-press-event", lambda _, e: self.record_macro(e))

    def stop_recording_macro(self):
        self.set_action_sensitivity([True, False, True])

        self.window.disconnect(self.handler_id)

    def playback_macro(self):
        for event in self.macro:
            event.put()

    def record_macro(self, event):
        self.macro.append(event.copy())

    def set_action_sensitivity(self, sensitive):
        for i, v in enumerate(["MacroStartRecording", "MacroStopRecording", "MacroPlayback"]):
            self.action_group.get_action(v).set_sensitive(sensitive[i])
