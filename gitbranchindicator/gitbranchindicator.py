# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import os

import gi

gi.require_version("Ggit", "1.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pluma", "1.0")
from gi.repository import GdkPixbuf, GObject, Gtk, Pango, Pluma, Ggit


class GitBranchIndicatorPlugin(GObject.Object, Pluma.WindowActivatable):
    __gtype_name__ = "GitBranchIndicatorPlugin"

    window = GObject.Property(type=Pluma.Window)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        Ggit.init()

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "icons/git-branch-light.svg" if self.is_dark_theme() else "icons/git-branch-dark.svg"),
            *Gtk.IconSize.lookup(Gtk.IconSize.SMALL_TOOLBAR)[1:], True)
        image = Gtk.Image.new_from_pixbuf(pixbuf)

        self.label = Gtk.Label.new(None)
        self.label.set_max_width_chars(40)
        self.label.set_ellipsize(Pango.EllipsizeMode.END)

        self.hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 2)
        self.hbox.pack_start(image, False, False, 0)
        self.hbox.pack_start(self.label, True, True, 0)
        self.hbox.show_all()
        self.hbox.hide()

        self.window.get_statusbar().pack_start(self.hbox, False, False, 18)

        self.handler_ids = [
            self.window.connect("active-tab-changed", lambda _, t: self.show_git_branch(t)),
            self.window.connect("active-tab-state-changed", lambda w: self.show_git_branch(w.get_active_tab())),
            self.window.connect("tab-removed", lambda *_: self.hide_if_no_tabs())
        ]

    def do_deactivate(self):
        for handler_id in self.handler_ids:
            self.window.disconnect(handler_id)

        self.hbox.destroy()

    def do_update_state(self):
        pass

    # https://lzone.de/blog/Detecting-a-Dark-Theme-in-GTK
    def is_dark_theme(self):
        style = self.window.get_style_context()
        found, txt_color = style.lookup_color("theme_text_color")
        if not found:
            txt_color = style.get_color(Gtk.StateFlags.NORMAL)

        found, bg_color = style.lookup_color("theme_bg_color")
        if not found:
            # TODO: `get_background_color()` is deprecated, rewrite it in the future
            # https://gitlab.gnome.org/GNOME/pygobject/-/issues/119 and
            # https://www.titanwolf.org/Network/q/11077cf0-7647-485d-a48d-8c17a2c26788/y
            bg_color = style.get_background_color(Gtk.StateFlags.NORMAL)

        txt_avg = txt_color.blue / 256 + txt_color.green / 256 + txt_color.red / 256
        bg_avg = bg_color.blue / 256 + bg_color.green / 256 + bg_color.red / 256

        return txt_avg > bg_avg

    def get_current_git_branch(self, location):
        if (repo_location := Ggit.Repository.discover(location)) is not None:
            if (repo := Ggit.Repository.open(repo_location)) is not None:
                if (head_ref := repo.lookup_reference("HEAD")) is not None:
                    if (symbolic_ref := head_ref.get_symbolic_target()) is not None:
                        return os.path.basename(symbolic_ref)

    def show_git_branch(self, tab):
        doc = tab.get_document()
        if (location := doc.get_location()) is not None and location.query_exists():
            try:
                if (branch := self.get_current_git_branch(location)) is not None:
                    self.label.set_text(branch)
                    self.hbox.show()
                    return
            except gi.repository.GLib.Error:
                pass

        self.hbox.hide()

    def hide_if_no_tabs(self):
        if self.window.get_active_tab() is None:
            self.hbox.hide()
