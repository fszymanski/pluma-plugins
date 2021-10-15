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

gettext.textdomain('pluma-togglepanel')
_ = gettext.gettext

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Pluma', '1.0')
from gi.repository import GObject, Gtk, Pluma


class TogglePanelPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'TogglePanelPlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        side_button = Gtk.ToggleButton.new()
        side_button.set_image(Gtk.Image.new_from_icon_name('go-first-symbolic', Gtk.IconSize.SMALL_TOOLBAR))
        side_button.set_relief(Gtk.ReliefStyle.NONE)
        side_button.set_focus_on_click(False)
        side_button.set_tooltip_text(_('Show/hide the side panel'))

        bottom_button = Gtk.ToggleButton.new()
        bottom_button.set_image(Gtk.Image.new_from_icon_name('go-bottom-symbolic', Gtk.IconSize.SMALL_TOOLBAR))
        bottom_button.set_relief(Gtk.ReliefStyle.NONE)
        bottom_button.set_focus_on_click(False)
        bottom_button.set_tooltip_text(_('Show/hide the bottom panel'))

        self.hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.hbox.pack_start(side_button, False, False, 0)
        self.hbox.pack_start(bottom_button, False, False, 0)
        self.hbox.show_all()

        statusbar = self.window.get_statusbar()
        statusbar.pack_end(self.hbox, False, False, 0)

        side_panel = self.window.get_side_panel()
        side_panel.connect('notify::visible', lambda p, v: side_button.set_active(p.get_property('visible')))
        side_button.connect('toggled', lambda b: side_panel.set_property('visible', b.get_active()))

        bottom_panel = self.window.get_bottom_panel()
        bottom_panel.connect('notify::visible', lambda p, v: bottom_button.set_active(p.get_property('visible')))
        bottom_button.connect('toggled', lambda b: bottom_panel.set_property('visible', b.get_active()))

    def do_deactivate(self):
        self.hbox.destroy()

    def do_update_state(self):
        pass

# vim: ft=python3 ts=4 et
