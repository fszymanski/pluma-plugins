# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2024 Filip Szymański <fszymanski.pl@gmail.com>

import os

from gi.repository import GLib, GObject


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
            flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD|GLib.SpawnFlags.SEARCH_PATH,
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
