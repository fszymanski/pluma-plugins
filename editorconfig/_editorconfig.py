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
from gi.repository import GLib, GObject, Peas, Pluma

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

        for name, val in config.items():
            if name == 'indent_style':
                if val == 'tab':
                    view.set_insert_spaces_instead_of_tabs(False)
                elif val == 'space':
                    view.set_insert_spaces_instead_of_tabs(True)

            if name == 'indent_size':
                if val == 'tab' and 'tab_width' in config:
                    view.set_tab_width(int(config['tab_width']))
                else:
                    try:
                        view.set_tab_width(int(val))
                    except ValueError:
                        pass

            if name == 'tab_width':
                view.set_tab_width(int(val))

            if name == 'end_of_line':
                if val == 'lf':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.LF)
                elif val == 'cr':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.CR)
                elif val == 'crlf':
                    doc.set_property('newline-type', Pluma.DocumentNewlineType.CR_LF)

            if name == 'trim_trailing_whitespace':
                pass  # TODO

            if name == 'insert_final_newline':
                pass  # TODO

            if name == 'max_line_length':
                view.set_right_margin_position(int(val))

# vim: ts=4 et
