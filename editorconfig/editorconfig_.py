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

gi.require_version('Pluma', '1.0')

from gi.repository import Gio, GObject, Pluma

import editorconfig


class EditorConfigPlugin(GObject.Object, Pluma.ViewActivatable):
    __gtype_name__ = 'EditorConfigPlugin'

    view = GObject.Property(type=Pluma.View)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        doc = self.view.get_buffer()
        if not hasattr(doc, 'editorconfig_handler'):
            doc.editorconfig_handler = doc.connect('loaded', self.apply_editorconfig)

    def do_deactivate(self):
        app = Pluma.App.get_default()
        window = app.get_active_window()
        for doc in window.get_documents():
            if hasattr(doc, 'editorconfig_handler'):
                doc.disconnect(doc.editorconfig_handler)
                del doc.editorconfig_handler

            if hasattr(doc, 'editorconfig_trim_trailing_whitespace_handler'):
                doc.disconnect(doc.editorconfig_trim_trailing_whitespace_handler)
                del doc.editorconfig_trim_trailing_whitespace_handler

    def do_update_state(self):
        pass

    def parse_editorconfig(self, doc):
        location = doc.get_location()
        if location is not None and location.query_exists():
            try:
                return editorconfig.get_properties(location.get_path())
            except editorconfig.EditorConfigError:
                pass

    def apply_editorconfig(self, doc, arg):
        config = self.parse_editorconfig(doc)
        if config is None:
            return

        for name, value in config.items():
            if name == 'indent_style':
                if value == 'tab':
                    self.view.set_insert_spaces_instead_of_tabs(False)
                elif value == 'space':
                    self.view.set_insert_spaces_instead_of_tabs(True)
            elif name == 'indent_size':
                if value == 'tab' and 'tab_width' in config:
                    self.view.set_tab_width(int(config['tab_width']))
                else:
                    try:
                        self.view.set_tab_width(int(value))
                    except ValueError:
                        pass
            elif name == 'tab_width':
                self.view.set_tab_width(int(value))
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
                    if not hasattr(doc, 'editorconfig_trim_trailing_whitespace_handler'):
                        doc.editorconfig_trim_trailing_whitespace_handler = doc.connect(
                            'save', self.trim_trailing_whitespace)
            elif name == 'max_line_length':
                self.view.set_right_margin_position(int(value))

    def trim_trailing_whitespace(self, doc, uri, encoding, flags):
        for linenr in range(0, doc.get_line_count()):
            start = doc.get_iter_at_line(linenr)

            end = start.copy()
            if not end.ends_line():
                end.forward_to_line_end()

            line = doc.get_text(start, end, False).rstrip()
            start.forward_chars(len(line))

            if not start.equal(end):
                doc.delete(start, end)

# vim: ts=4 et
