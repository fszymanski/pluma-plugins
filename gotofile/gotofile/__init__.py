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

import os

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('PeasGtk', '1.0')
gi.require_version('Pluma', '1.0')
from gi.repository import Gio, GObject, Gtk, PeasGtk, Pluma

from .popup import Popup

ui_str = """
<ui>
    <menubar name='MenuBar'>
        <menu name='FileMenu' action='File'>
            <placeholder name='FileOps_2'>
                <menuitem name='GoToFile' action='GoToFile'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class GoToFilePlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = 'GoToFilePlugin'

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = Gtk.Action.new('GoToFile', _('Go to File...'))
        action.set_icon_name('document-open')
        action.connect('activate', lambda a: self.goto_file())

        self.action_group = Gtk.ActionGroup.new('GoToFilePluginActions')
        self.action_group.add_action_with_accel(action, '<Ctrl><Alt>o')

        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, -1)
        self.merge_id = manager.add_ui_from_string(ui_str)

    def do_deactivate(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()

    def do_update_state(self):
        pass

    def goto_file(self):
        popup = Popup(self.window)
        popup.show_all()


class GoToFileConfigurable(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'GoToFileConfigurable'

    def __init__(self):
        super().__init__()

    def do_create_configure_widget(self):
        settings = Gio.Settings.new('org.mate.pluma.plugins.gotofile')

        builder = Gtk.Builder()
        builder.add_from_file(os.path.join(self.plugin_info.get_data_dir(), 'gotofile', 'preferences.ui'))

        bookmarks_checkbox = builder.get_object('bookmarks_checkbox')
        bookmarks_checkbox.set_active(settings.get_boolean('bookmarks'))
        bookmarks_checkbox.connect('toggled', lambda b: settings.set_boolean('bookmarks', b.get_active()))

        desktop_dir_checkbox = builder.get_object('desktop_dir_checkbox')
        desktop_dir_checkbox.set_active(settings.get_boolean('desktop-dir'))
        desktop_dir_checkbox.connect('toggled', lambda b: settings.set_boolean('desktop-dir', b.get_active()))

        file_browser_root_dir_checkbox = builder.get_object('file_browser_root_dir_checkbox')
        file_browser_root_dir_checkbox.set_active(settings.get_boolean('file-browser-root-dir'))
        file_browser_root_dir_checkbox.connect('toggled', lambda b: settings.set_boolean('file-browser-root-dir',
                                                                                         b.get_active()))

        home_dir_checkbox = builder.get_object('home_dir_checkbox')
        home_dir_checkbox.set_active(settings.get_boolean('home-dir'))
        home_dir_checkbox.connect('toggled', lambda b: settings.set_boolean('home-dir', b.get_active()))

        open_docs_dir_checkbox = builder.get_object('open_docs_dir_checkbox')
        open_docs_dir_checkbox.set_active(settings.get_boolean('open-docs-dir'))
        open_docs_dir_checkbox.connect('toggled', lambda b: settings.set_boolean('open-docs-dir', b.get_active()))

        recent_files_checkbox = builder.get_object('recent_files_checkbox')
        recent_files_checkbox.set_active(settings.get_boolean('recent-files'))
        recent_files_checkbox.connect('toggled', lambda b: settings.set_boolean('recent-files', b.get_active()))

        return builder.get_object('preferences_widget')

# vim: ts=4 et
