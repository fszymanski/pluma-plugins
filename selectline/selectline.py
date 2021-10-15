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

import gettext

gettext.textdomain('pluma-selectline')
_ = gettext.gettext

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import GObject, Gtk, Pluma

ui_str = """
<ui>
    <menubar name='MenuBar'>
        <menu name='EditMenu' action='Edit'>
            <placeholder name='EditOps_2'>
                <menuitem name='SelectLine' action='SelectLine'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class SelectLinePlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'SelectLinePlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = Gtk.Action.new('SelectLine', _('Select Line'))
        action.connect('activate', lambda a: self.select_line())

        self.action_group = Gtk.ActionGroup.new('SelectLinePluginActions')
        self.action_group.add_action_with_accel(action, '<Ctrl>t')

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

# vim: ft=python3 ts=4 et
