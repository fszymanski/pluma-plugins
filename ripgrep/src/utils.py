# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import os

from gi.repository import GLib, GObject


class StatusbarFlashMessage:
    def __init__(self):
        self.__timeout = 0
        self.__context_id = None
        self.__msg_id = None

    def __remove_message_timeout(self, statusbar):
        statusbar.remove(self.__context_id, self.__msg_id)

        self.__timeout = 0

    def flash_message(self, statusbar, msg):
        if self.__timeout > 0:
            GLib.source_remove(self.__timeout)

            self.__remove_message_timeout(statusbar)

        self.__context_id = statusbar.get_context_id("ripgrep_plugin_message")
        self.__msg_id = statusbar.push(self.__context_id, msg)

        self.__timeout = GLib.timeout_add(3000, self.__remove_message_timeout, statusbar)


class AsyncSpawn(GObject.GObject):
    __gsignals__ = {
        "process-started": (GObject.SignalFlags.RUN_LAST, None, ()),
        "process-finished": (GObject.SignalFlags.RUN_LAST, None, (int,)),
        "stdout-data": (GObject.SignalFlags.RUN_LAST, None, (str,)),
        "stderr-data": (GObject.SignalFlags.RUN_LAST, None, (str,))
    }

    def __init__(self):
        super().__init__()

    def run(self, cmd):
        pid, _, stdout, stderr = GLib.spawn_async(
            cmd,
            flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD | GLib.SpawnFlags.SEARCH_PATH,
            standard_output=True,
            standard_error=True)

        self.emit("process-started")

        fout = os.fdopen(stdout, "r")
        ferr = os.fdopen(stderr, "r")

        GLib.child_watch_add(GLib.PRIORITY_DEFAULT_IDLE, pid, self.on_finished)
        GLib.io_add_watch(fout, GLib.IO_IN, self.on_stdout)
        GLib.io_add_watch(ferr, GLib.IO_IN, self.on_stderr)

        return pid

    def on_finished(self, pid, *_):
        self.emit("process-finished", pid)

    def on_stdout(self, fobj, _):
        self.emit("stdout-data", fobj.read().rstrip("\n"))
        return True

    def on_stderr(self, fobj, _):
        self.emit("stderr-data", fobj.read())
        return True

# vim: ft=python3
