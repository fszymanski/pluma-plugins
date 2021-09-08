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

try:
    import gettext

    gettext.bindtextdomain('pluma-plugins')
    gettext.textdomain('pluma-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s

import re
import webbrowser

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('PeasGtk', '1.0')
gi.require_version('Pluma', '1.0')
from gi.repository import Gio, GObject, Gtk, PeasGtk, Pluma

WEB_SEARCH_SCHEMA = 'org.mate.pluma.plugins.websearch'
WORD_BOUNDARY_RE = re.compile(r'\s')


class WebSearchPlugin(GObject.Object, Pluma.ViewActivatable):
    __gtype_name__ = 'WebSearchPlugin'

    view = GObject.Property(type=Pluma.View)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        if not hasattr(self.view, 'web_search_handler'):
            self.view.web_search_handler = self.view.connect('populate-popup', self.append_search_to_context_menu)

    def do_deactivate(self):
        app = Pluma.App.get_default()
        window = app.get_active_window()
        for view in window.get_views():
            if hasattr(view, 'web_search_handler'):
                view.disconnect(view.web_search_handler)
                del view.web_search_handler

    def do_update_state(self):
        pass

    def append_search_to_context_menu(self, view, popup):
        menu_item = Gtk.MenuItem.new_with_label(_('Web Search'))
        menu_item.connect('activate', lambda m: self.search())
        menu_item.show()

        separator = Gtk.SeparatorMenuItem.new()
        separator.show()

        popup.append(separator)
        popup.append(menu_item)

    def get_search_query(self):
        doc = self.view.get_buffer()
        if doc.get_has_selection():
            start, end = doc.get_selection_bounds()
        else:
            start = doc.get_iter_at_mark(doc.get_insert())
            while start.backward_char():
                if WORD_BOUNDARY_RE.match(start.get_char()) is not None:
                    start.forward_char()
                    break

            end = start.copy()
            while end.forward_char():
                if WORD_BOUNDARY_RE.match(end.get_char()) is not None:
                    break

        return doc.get_text(start, end, False)

    def search(self):
        query = self.get_search_query()
        if query:
            settings = Gio.Settings.new(WEB_SEARCH_SCHEMA)
            try:
                url = (
                    (settings.get_default_value('query-url').get_string() % query)
                    if not settings.get_string('query-url')
                    else (settings.get_string('query-url') % query))
            except TypeError:
                return

            webbrowser.open(url)


class WebSearchConfigurable(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'WebSearchConfigurable'

    def __init__(self):
        super().__init__()

    def do_create_configure_widget(self):
        settings = Gio.Settings.new(WEB_SEARCH_SCHEMA)

        query_label = Gtk.Label.new(None)
        query_label.set_halign(Gtk.Align.START)
        query_label.set_markup('<b>{}</b>'.format(_('Query URL:')))

        entry = Gtk.Entry.new()
        entry.set_width_chars(40)
        entry.set_text(settings.get_string('query-url'))

        entry.connect('changed', lambda e: settings.set_string('query-url', entry.get_text()))

        button = Gtk.Button.new_from_icon_name('edit-clear', Gtk.IconSize.MENU)
        button.connect('clicked', lambda b: entry.set_text(''))

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        hbox.pack_start(entry, True, True, 0)
        hbox.pack_start(button, False, False, 0)

        info_label = Gtk.Label.new(None)
        info_label.set_halign(Gtk.Align.START)
        info_label.set_markup('<i>{}</i>'.format(_('URL with %s in place of query')))

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        vbox.pack_start(query_label, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(info_label, False, False, 0)

        return vbox

# vim: ts=4 et
