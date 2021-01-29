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
from gi.repository import Gio, GLib, GObject, Peas, Pluma

import editorconfig


class EditorConfigPlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'EditorConfigPlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        window = self.object

        window.connect('active-tab-state-changed', self.apply_config)

    def do_deactivate(self):
        pass

    def do_update_state(self):
        pass

    def parse_config(self, doc):
        uri = doc.get_uri()
        if uri is not None and Pluma.utils_uri_has_file_scheme(uri):
            try:
                return editorconfig.get_properties(GLib.filename_from_uri(uri)[0])
            except editorconfig.EditorConfigError:
                pass

    def apply_config(self, window):
        tab = window.get_active_tab()
        doc = tab.get_document()
        config = self.parse_config(doc)
        if config is None:
            return

        view = tab.get_view()

        for name, value in config.items():
            if name == 'indent_style':
                if value == 'tab':
                    view.set_insert_spaces_instead_of_tabs(False)
                elif value == 'space':
                    view.set_insert_spaces_instead_of_tabs(True)
            elif name == 'indent_size':
                if value == 'tab' and 'tab_width' in config:
                    view.set_tab_width(int(config['tab_width']))
                else:
                    try:
                        view.set_tab_width(int(value))
                    except ValueError:
                        pass
            elif name == 'tab_width':
                view.set_tab_width(int(value))
            elif name == 'end_of_line':
                if value == 'lf':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.LF)
                elif value == 'cr':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.CR)
                elif value == 'crlf':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.CR_LF)
            elif name == 'trim_trailing_whitespace':
                settings = Gio.Settings.new('org.mate.pluma')
                if 'trailsave' not in settings.get_value('active-plugins'):
                    if not hasattr(doc, 'editorconfig_trim_trailing_whitespace'):
                        doc.editorconfig_trim_trailing_whitespace = doc.connect(
                            'save', self.trim_trailing_whitespace)
            elif name == 'insert_final_newline':
                if not hasattr(doc, 'editorconfig_insert_final_newline'):
                    doc.editorconfig_insert_final_newline = doc.connect('save',
                                                                        self.insert_final_newline)
            elif name == 'max_line_length':
                view.set_right_margin_position(int(value))

    def trim_trailing_whitespace(self, doc, *args):
        for linenr in range(0, doc.get_line_count()):
            start = doc.get_iter_at_line(linenr)

            end = start.copy()
            if not end.ends_line():
                end.forward_to_line_end()

            line = doc.get_text(start, end, False).rstrip()
            start.forward_chars(len(line))

            if not start.equal(end):
                doc.delete(start, end)

    def insert_final_newline(self, doc, *args):
        pass  # TODO

# vim: ts=4 et