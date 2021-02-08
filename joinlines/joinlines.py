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
        <menu name='EditMenu' action='Edit'>
            <placeholder name='EditOps_1'>
                <menuitem name='JoinLines' action='JoinLines'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class JoinLinesPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'JoinLinesPlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.window = self.object
        manager = self.window.get_ui_manager()

        action = Gtk.Action.new('JoinLines', _('Join Lines'))
        action.connect('activate', lambda a: self.join_lines())

        self.action_group = Gtk.ActionGroup.new('JoinLinesPluginActions')
        self.action_group.add_action_with_accel(action, '<Ctrl>j')

        manager.insert_action_group(self.action_group, -1)
        self.merge_id = manager.add_ui_from_string(ui_str)

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def do_update_state(self):
        pass

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

# vim: ts=4 et
