import os

from gi.repository import GLib, GObject


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
            pid, _, stdout, stderr = GLib.spawn_async(
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

    def on_process_done(self, pid, *_):
        self.emit("process-done", pid)

    def on_stdout(self, fobj, _):
        self.emit("stdout", fobj.readline())
        return True

    def on_stderr(self, fobj, _):
        self.emit("stderr", fobj.readline())
        return True
