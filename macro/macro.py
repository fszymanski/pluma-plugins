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

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import GObject, Gtk, Pluma

ui_str = """
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
    __gtype_name__ = 'MacroPlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.action_group = Gtk.ActionGroup('PlumaMacroPluginActions')
        self.action_group.add_actions([
            ('ToolsMacro', None, 'Macro', None, None, None),
            ('MacroStartRecording', Gtk.STOCK_MEDIA_RECORD, 'Start Recording', None, None, lambda _: self.start_recording_macro()),
            ('MacroStopRecording', Gtk.STOCK_MEDIA_STOP, 'Stop Recording', None, None, lambda _: self.stop_recording_macro()),
            ('MacroPlayback', Gtk.STOCK_MEDIA_PLAY, 'Playback', '<Ctrl><Alt>m', None, lambda _: self.playback_macro())
        ])

        self.set_action_sensitivity([True, False, False])

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group)
        self.merge_id = manager.add_ui_from_string(ui_str)

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def do_update_state(self):
        pass

    def start_recording_macro(self):
        self.macro = []

        self.set_action_sensitivity([False, True, False])

        self.handler_id = self.window.connect('key-press-event', lambda _, e: self.record_macro(e))

    def stop_recording_macro(self):
        self.set_action_sensitivity([True, False, True])

        self.window.disconnect(self.handler_id)

    def playback_macro(self):
        for event in self.macro:
            event.put()

    def record_macro(self, event):
        self.macro.append(event.copy())

    def set_action_sensitivity(self, sensitive):
        for i, v in enumerate(['MacroStartRecording', 'MacroStopRecording', 'MacroPlayback']):
            self.action_group.get_action(v).set_sensitive(sensitive[i])

# vim: ft=python3 ts=4 et
