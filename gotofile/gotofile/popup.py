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

from gi.repository import Gtk, Pango

from .source import *

try:
    import gettext

    gettext.bindtextdomain('pluma-plugins')
    gettext.textdomain('pluma-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s


class Popup(Gtk.Window):
    __gtype_name__ = 'Popup'

    def __init__(self, parent):
        super().__init__(default_height=360,
                         default_width=500,
                         destroy_with_parent=True,
                         modal=True,
                         title=_('Go To File'),
                         transient_for=parent,
                         window_position=Gtk.WindowPosition.CENTER_ON_PARENT)

        filter_entry = Gtk.SearchEntry.new()
        filter_entry.grab_focus_without_selecting()
        filter_entry.set_placeholder_text(_('Search...'))

        scroller = Gtk.ScrolledWindow.new(None, None)

        filename_label = Gtk.Label.new(None)
        filename_label.set_halign(Gtk.Align.START)
        filename_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        vbox.pack_start(filter_entry, False, False, 0)
        vbox.pack_start(scroller, True, True, 0)
        vbox.pack_start(filename_label, False, False, 0)
        self.add(vbox)

# vim: ts=4 et
