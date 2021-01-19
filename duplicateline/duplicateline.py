# -*- coding: utf-8 -*-
#
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
            <menuitem name='DuplicateLine' action='DuplicateLine'/>
         </placeholder>
       </menu>
    </menubar>
</ui>
"""


class DuplicateLinePlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'DuplicateLinePlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.window = self.object
        manager = self.window.get_ui_manager()

        action = Gtk.Action.new('DuplicateLine', _('Duplicate Line/Selection'))
        action.connect('activate', lambda _: self.on_duplicate_line())

        self.action_group = Gtk.ActionGroup(name='DuplicateLinePluginActions')
        self.action_group.add_action_with_accel(action, '<Ctrl><Shift>D')

        manager.insert_action_group(self.action_group, -1)
        self.merge_id = manager.add_ui_from_string(ui_str)

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def on_duplicate_line(self):
        doc = self.window.get_active_document()
        if doc is None:
            return

        if doc.get_has_selection():
            start, end = doc.get_selection_bounds()
            if start.get_line() != end.get_line():
                start.set_line_offset(0)
                if not end.ends_line():
                    end.forward_to_line_end()

                lines = doc.get_text(start, end, False)
                if lines[-1] != '\n':
                    sel = f'\n{lines}'

                doc.insert(end, lines)
            else:
                sel = doc.get_text(start, end, False)

                doc.move_mark_by_name('selection_bound', start)
                doc.insert(end, sel)
        else:
            start = doc.get_iter_at_mark(doc.get_insert())
            start.set_line_offset(0)

            end = doc.get_iter_at_mark(doc.get_insert())
            end.forward_to_line_end()

            curr_line = doc.get_text(start, end, False)
            doc.insert(end, f'\n{curr_line}')

# vim: ts=4 et
