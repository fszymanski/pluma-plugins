# Copyright (C) 2023 Filip Szymański <fszymanski.pl@gmail.com>
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

import os

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Pango, Pluma

ui_str = """
<ui>
    <menubar name='MenuBar'>
        <menu name='FileMenu' action='File'>
            <placeholder name='FileOps_2'>
                <menuitem name='FileQuickOpenMenu' action='FileQuickOpen'/>
            </placeholder>
        </menu>
    </menubar>
</ui>
"""

DEFAULT_COMMAND = ["find", os.environ['HOME'], "-type", "f"]


class AsyncSpawn(GObject.GObject):
    __gsignals__ = {
        "process-done": (GObject.SignalFlags.RUN_LAST, None, (int,)),
        "stdout": (GObject.SignalFlags.RUN_LAST, None, (str,)),
        "stderr": (GObject.SignalFlags.RUN_LAST, None, (str,))
    }

    def __init__(self):
        super().__init__()

    def run(self, cmd):
        try:
            pid, stdin, stdout, stderr = GLib.spawn_async(
                cmd,
                flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD|GLib.SpawnFlags.SEARCH_PATH,
                standard_output=True,
                standard_error=True)
        except GLib.Error as e:
            print(f"Error: Failed to execute '{' '.join(cmd)}': {e}")  # debug

        fout = os.fdopen(stdout, "r")
        ferr = os.fdopen(stderr, "r")

        GLib.child_watch_add(GLib.PRIORITY_DEFAULT_IDLE, pid, self.on_process_done)
        GLib.io_add_watch(fout, GLib.IO_IN, self.on_stdout)
        GLib.io_add_watch(ferr, GLib.IO_IN, self.on_stderr)

        return pid

    def on_process_done(self, pid, wait_status, *data):
        self.emit("process-done", pid)

    def on_stdout(self, fobj, cond):
        self.emit("stdout", fobj.readline())
        return True

    def on_stderr(self, fobj, cond):
        self.emit("stderr", fobj.readline())
        return True


class Popup(Gtk.Dialog):
    __gtype_name__ = "QuickOpenPopup"

    def __init__(self, window):
        super().__init__(parent=window,
                         title="Quick Open",
                         default_width=800,
                         default_height=600,
                         flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                         buttons=("_Cancel", Gtk.ResponseType.CANCEL, "_Open", Gtk.ResponseType.ACCEPT))

        self._window = window

        cancel_button, open_button = self.get_action_area().get_children()
        cancel_button.set_image(Gtk.Image.new_from_icon_name("process-stop", Gtk.IconSize.BUTTON))
        open_button.set_image(Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.BUTTON))

        filter_entry = Gtk.SearchEntry(placeholder_text="Search...")
        filter_entry.grab_focus_without_selecting()

        model = Gtk.ListStore(str)
        file_filter = model.filter_new()
        file_filter.set_visible_func(self.file_filter_func, filter_entry)
        file_view = Gtk.TreeView(activate_on_single_click=True, headers_visible=False, model=file_filter)

        filter_entry.connect("search-changed", lambda _: file_filter.refilter())

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(cell_renderer=renderer, text=0)
        file_view.append_column(column)

        scroller = Gtk.ScrolledWindow()
        scroller.add(file_view)

        selection = file_view.get_selection()

        filter_entry.connect("search-changed", self.select_first_row, selection)

        open_button.connect("clicked", self.open_file, selection)
        file_view.connect("row-activated", self.open_file, selection)

        file_label = Gtk.Label(ellipsize=Pango.EllipsizeMode.MIDDLE, halign=Gtk.Align.START)

        selection.connect("changed", self.on_selection_changed, file_label)

        vbox = self.get_content_area()
        vbox.pack_start(filter_entry, False, False, 0)
        vbox.pack_start(scroller, True, True, 0)
        vbox.pack_start(file_label, False, False, 0)

        self.connect("key-press-event", self.destroy_on_escape_key)

        spawn = AsyncSpawn()
        spawn.connect("process-done", self.on_process_done, selection)
        spawn.connect("stdout", self.on_stdout, model)
        spawn.connect("stderr", self.on_stderr)

        pid = spawn.run(DEFAULT_COMMAND)

        cancel_button.connect("clicked", self.cancel_process, pid)

        self.show_all()

    def file_filter_func(self, model, iter_, filter_entry):
        needle = filter_entry.get_text().strip()
        if not needle:
            return True

        haystack = model.get_value(iter_, 0)
        return GLib.str_match_string(needle, haystack, True)

    def destroy_on_escape_key(self, dialog, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

        return False

    def on_selection_changed(self, selection, file_label):
        model, iter_ = selection.get_selected()
        if iter_ is not None:
            file_label.set_text(model.get_value(iter_, 0))
        else:
            file_label.set_text("")

    def select_first_row(self, filter_entry, selection):
        selection.select_path(Gtk.TreePath.new_first())

    def cancel_process(self, button, pid):
        GLib.spawn_close_pid(pid)

        self.destroy()

    def open_file(self, *args):
        model, iter_ = args[-1].get_selected()  # args[-1] = selection
        if iter_ is not None:
            path = model.get_value(iter_, 0)
            location = Gio.file_new_for_path(path)
            if location.query_exists():
                if (tab := self._window.get_tab_from_location(location)) is None:
                    self._window.create_tab_from_uri(location.get_uri(), Pluma.encoding_get_utf8(), 0, False, True)
                else:
                    self._window.set_active_tab(tab)

            self.destroy()

    def on_process_done(self, sender, pid, selection):
        self.select_first_row(None, selection)

        GLib.spawn_close_pid(pid)

    def on_stdout(self, sender, line, model):
        model.append([line.rstrip()])

    def on_stderr(self, sender, line):
        print(f"Error: {line.rstrip()}")  # debug


class QuickOpenPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "QuickOpenPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        action = Gtk.Action(name="FileQuickOpen", label="Quick Open", icon_name="document-open")
        action.connect("activate", lambda _: self.search_for_files())

        self.action_group = Gtk.ActionGroup(name="FileQuickOpenPluginActions")
        self.action_group.add_action_with_accel(action, "<Ctrl><Alt>o")

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

    def search_for_files(self):
        Popup(self.window)

# vim: ft=python3 ts=4 et
