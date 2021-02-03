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
gi.require_version('Peas', '1.0')

from gi.repository import GObject, Gtk, Peas

try:
    import gettext

    gettext.bindtextdomain('pluma-plugins')
    gettext.textdomain('pluma-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s

ui_str = """
<ui>
    <menubar name='MenuBar'>
        <menu name='ToolsMenu' action='Tools'>
            <placeholder name='ToolsOps_2'>
                <menu name='Macro' action='Macro'>
                    <menuitem name='StartRecording' action='StartRecording'/>
                    <menuitem name='StopRecording' action='StopRecording'/>
                    <menuitem name='Playback' action='Playback'/>
                </menu>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class MacroPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'MacroPlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.window = self.object
        manager = self.window.get_ui_manager()

        self.action_group = Gtk.ActionGroup.new('MacroPluginActions')
        self.action_group.add_actions([
            ('Macro', None, _('Macro'), None, None, None),
            ('StartRecording', Gtk.STOCK_MEDIA_RECORD, _('Start Recording'), None, None, lambda a: self.start_recording_macro()),
            ('StopRecording', Gtk.STOCK_MEDIA_STOP, _('Stop Recording'), None, None, lambda a: self.stop_recording_macro()),
            ('Playback', Gtk.STOCK_MEDIA_PLAY, _('Playback'), '<Ctrl><Alt>m', None, lambda a: self.playback_macro())
        ])

        self.set_action_sensitivity([True, False, False])

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

        self.handler_id = self.window.connect('key-press-event', self.record_macro)

    def stop_recording_macro(self):
        self.set_action_sensitivity([True, False, True])

        self.window.disconnect(self.handler_id)

    def playback_macro(self):
        for event in self.macro:
            event.put()

    def record_macro(self, window, event):
        self.macro.append(event.copy())

    def set_action_sensitivity(self, sensitive):
        for i, v in enumerate(['StartRecording', 'StopRecording', 'Playback']):
            self.action_group.get_action(v).set_sensitive(sensitive[i])

# vim: ts=4 et
