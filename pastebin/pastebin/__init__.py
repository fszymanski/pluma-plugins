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

from .pastebindialog import PastebinDialog

ui_str = """
<ui>
    <menubar name='MenuBar'>
        <menu name='ToolsMenu' action='Tools'>
            <placeholder name='ToolsOps_1'>
                <menuitem name='UploadToPastebin' action='UploadToPastebin'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class PastebinPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'PastebinPlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = action = Gtk.Action(name='UploadToPastebin', label='Upload to Pastebin...')
        action.connect('activate', lambda _: PastebinDialog(self.window))

        self.action_group = Gtk.ActionGroup(name='PastebinPluginActions')
        self.action_group.add_action_with_accel(action, None)

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, -1)
        self.merge_id = manager.add_ui_from_string(ui_str)

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def do_update_state(self):
        view = self.window.get_active_view()
        self.action_group.set_sensitive(bool(view))

# vim: ft=python3 ts=4 et
