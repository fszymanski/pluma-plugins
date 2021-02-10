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

import locale
locale.setlocale(locale.LC_ALL, '')

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Peas', '1.0')
gi.require_version('PeasGtk', '1.0')

from gi.repository import Gio, GObject, Gtk, Peas, PeasGtk

from .popup import Popup

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
        <menu name='FileMenu' action='File'>
            <placeholder name='FileOps_2'>
                <menuitem name='GoToFile' action='GoToFile'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""


class GoToFilePlugin(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'GoToFilePlugin'

    object = GObject.Property(type=GObject.Object)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        self.window = self.object
        manager = self.window.get_ui_manager()

        action = Gtk.Action.new('GoToFile', _('Go to File...'))
        action.set_icon_name('document-open')
        action.connect('activate', lambda a: self.goto_file())

        self.action_group = Gtk.ActionGroup.new('GoToFilePluginActions')
        self.action_group.add_action_with_accel(action, '<Ctrl><Alt>o')

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

        self.settings = Gio.Settings.new('org.mate.pluma.plugins.gotofile')

    def do_create_configure_widget(self):
        look_label = Gtk.Label.new(None)
        look_label.set_markup('<b>{}</b>'.format(_('Look for files in:')))

        bookmarks_checkbox = Gtk.CheckButton.new_with_label(_('Directories you have bookmarked in Files/Caja'))
        bookmarks_checkbox.set_active(self.settings.get_boolean('bookmarks'))
        bookmarks_checkbox.connect('toggled', self.set_setting, 'bookmarks')

        desktop_dir_checkbox = Gtk.CheckButton.new_with_label(_('Desktop directory'))
        desktop_dir_checkbox.set_active(self.settings.get_boolean('desktop-dir'))
        desktop_dir_checkbox.connect('toggled', self.set_setting, 'desktop-dir')

        file_browser_root_dir_checkbox = Gtk.CheckButton.new_with_label(_('File browser root directory'))
        file_browser_root_dir_checkbox.set_active(self.settings.get_boolean('file-browser-root-dir'))
        file_browser_root_dir_checkbox.connect('toggled', self.set_setting, 'file-browser-root-dir')

        home_dir_checkbox = Gtk.CheckButton.new_with_label(_('Home directory'))
        home_dir_checkbox.set_active(self.settings.get_boolean('home-dir'))
        home_dir_checkbox.connect('toggled', self.set_setting, 'home-dir')

        open_docs_dir_checkbox = Gtk.CheckButton.new_with_label(_('Directory of the currently opened document(s)'))
        open_docs_dir_checkbox.set_active(self.settings.get_boolean('open-docs-dir'))
        open_docs_dir_checkbox.connect('toggled', self.set_setting, 'open-docs-dir')

        recent_files_checkbox = Gtk.CheckButton.new_with_label(_('Recently used files'))
        recent_files_checkbox.set_active(self.settings.get_boolean('recent-files'))
        recent_files_checkbox.connect('toggled', self.set_setting, 'recent-files')

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
        vbox.pack_start(look_label, False, False, 0)
        vbox.pack_start(bookmarks_checkbox, False, False, 0)
        vbox.pack_start(desktop_dir_checkbox, False, False, 0)
        vbox.pack_start(file_browser_root_dir_checkbox, False, False, 0)
        vbox.pack_start(home_dir_checkbox, False, False, 0)
        vbox.pack_start(open_docs_dir_checkbox, False, False, 0)
        vbox.pack_start(recent_files_checkbox, False, False, 0)

        return vbox

    def set_setting(self, button, key):
        self.settings.set_boolean(key, button.get_active())

# vim: ts=4 et
