import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

MAX_RECENTS = 200


def get_recent_files():
    manager = Gtk.RecentManager.get_default()
    items = manager.get_items()
    items.sort(key=lambda i: i.get_visited(), reverse=True)

    count = 0
    for item in items:
        if item.exists() and item.has_group("pluma"):
            yield Gio.File.new_for_uri(item.get_uri())

            count += 1
            if count >= MAX_RECENTS:
                break


def get_file_browser_virtual_root_dir():
    settings = Gio.Settings("org.mate.pluma")
    if "filebrowser" in settings.get_value("active-plugins"):
        settings = Gio.Settings("org.mate.pluma.plugins.filebrowser.on-load")
        uri = settings.get_string("virtual-root")
        return GLib.filename_from_uri(uri)[0]
