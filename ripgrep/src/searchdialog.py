# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import logging
import os
import re
import tempfile
from contextlib import suppress

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk

from .utils import AsyncSpawn, StatusbarFlashMessage

logger = logging.getLogger("pluma-ripgrep")

MAX_SEARCH_HISTORY = 100
RG_COMMAND = [
    "rg",
    "--color=never",
    "--no-heading",
    "--with-filename",
    "--line-number",
    "--column",
    "--smart-case",
    "--fixed-strings"
]
RG_SCHEMA = "org.mate.pluma.plugins.ripgrep"
RG_SEARCH_RESULT_RE = re.compile(r"^(?P<filename>.+):(?P<line>\d+):(?P<column>\d+):(?P<match>.+)$")
RG_TEMPFILE_RE = re.compile(r"^/tmp/pluma\.ripgrep\.")


@Gtk.Template(resource_path="/org/mate/pluma/plugins/ripgrep/ui/searchdialog.ui")
class SearchDialog(Gtk.Dialog, StatusbarFlashMessage):
    __gtype_name__ = "RipgrepSearchDialog"

    search_combo = Gtk.Template.Child()
    search_entry = Gtk.Template.Child()
    current_doc_radio = Gtk.Template.Child()
    folder_radio = Gtk.Template.Child()
    choose_folder_button = Gtk.Template.Child()
    find_button = Gtk.Template.Child()

    def __init__(self, window, panel):
        super().__init__(parent=window)
        StatusbarFlashMessage.__init__(self)

        self.window_ = window
        self.panel = panel
        self.tempfile_tracker = {}

        self.read_search_history()

        self.connect("destroy", lambda _: self.save_search_history())

        self.search_entry.connect("changed", lambda e: self.find_button.set_sensitive(e.get_text() != ""))
        self.current_doc_radio.connect(
            "toggled", lambda b: self.choose_folder_button.set_sensitive(not b.get_active()))

        self.spawn = AsyncSpawn()
        self.spawn.connect("process-started", lambda _: self.panel.clear())
        self.spawn.connect("process-finished", self.on_process_finished)
        self.spawn.connect("stdout-data", self.on_stdout_data)
        self.spawn.connect("stderr-data", self.on_stderr_data)

        self.show_all()

    def get_search_history(self):
        if (store := self.search_combo.get_model()) is not None:
            return [row[0] for row in store]

    def append_pattern_to_search_history(self, pattern):
        if (patterns := self.get_search_history()) is not None:
            with suppress(ValueError):
                patterns.remove(pattern)

            patterns.insert(0, pattern)

            self.search_combo.remove_all()

            count = 0
            for pattern in patterns:
                self.search_combo.append_text(pattern)

                count += 1
                if count >= MAX_SEARCH_HISTORY:
                    break

    def read_search_history(self):
        settings = Gio.Settings.new(RG_SCHEMA)
        patterns = settings.get_value("search-history").unpack()
        for pattern in patterns:
            self.search_combo.append_text(pattern)

    def save_search_history(self):
        settings = Gio.Settings.new(RG_SCHEMA)

        if (patterns := self.get_search_history()) is not None:
            settings.set_value("search-history", GLib.Variant("as", patterns))

    @Gtk.Template.Callback()
    def on_close_button_clicked(self, _):
        self.destroy()

    @Gtk.Template.Callback()
    def on_find_button_clicked(self, _):
        pattern = self.search_entry.get_text()
        self.append_pattern_to_search_history(pattern)

        path = None
        if self.current_doc_radio.get_active():
            if (doc := self.window_.get_active_document()) is not None:
                if (location := doc.get_location()) is not None and location.query_exists():
                    path = location.get_path()
                else:
                    start, end = doc.get_bounds()
                    text = doc.get_text(start, end, True)

                    with tempfile.NamedTemporaryFile(
                            mode="w", prefix="pluma.ripgrep.", dir="/tmp", delete=False) as f:
                        f.write(text)

                    path = f.name
        else:
            path = self.choose_folder_button.get_filename()

        if path is not None and os.path.exists(path):
            try:
                pid = self.spawn.run(RG_COMMAND + [pattern, path])
                if RG_TEMPFILE_RE.match(path) is not None:
                    self.tempfile_tracker[pid] = path

                self.panel.show()
            except GLib.Error as err:
                self.flash_message(self.window_.get_statusbar(), "Failed to start the 'rg' process")

                logger.error(err)

    def on_process_finished(self, _, pid):
        GLib.spawn_close_pid(pid)

        if pid in self.tempfile_tracker:
            with suppress(FileNotFoundError, OSError):
                os.remove(self.tempfile_tracker[pid])

            del self.tempfile_tracker[pid]

    def on_stdout_data(self, _, lines):
        doc = self.window_.get_active_document()

        store = self.panel.get_model()
        for line in lines.split("\n"):
            if (result := RG_SEARCH_RESULT_RE.search(line)) is not None:
                is_tempfile = RG_TEMPFILE_RE.match(result.group("filename")) is not None

                store.append([
                    doc.get_short_name_for_display() if is_tempfile else result.group("filename"),
                    result.group("line"),
                    result.group("column"),
                    result.group("match"),
                    doc if is_tempfile else None
                ])

    def on_stderr_data(self, _, lines):
        logger.error(lines)

# vim: ft=python3
