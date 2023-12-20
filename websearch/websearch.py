# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2021-2023 Filip Szymański <fszymanski.pl@gmail.com>

import os
import webbrowser

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("PeasGtk", "1.0")
gi.require_version("Pluma", "1.0")
from gi.repository import Gio, GObject, Gtk, PeasGtk, Pluma

WEB_SEARCH_SCHEMA = "org.mate.pluma.plugins.websearch"


class WebSearchPlugin(GObject.Object, Pluma.ViewActivatable):
    __gtype_name__ = "WebSearchPlugin"

    view = GObject.Property(type=Pluma.View)

    def __init__(self):
        super().__init__()

    def do_activate(self):
        if not hasattr(self.view, "web_search_handler_id"):
            self.view.web_search_handler_id = self.view.connect("populate-popup", self.append_search_to_context_menu)

    def do_deactivate(self):
        app = Pluma.App.get_default()
        window = app.get_active_window()
        for view in window.get_views():
            if hasattr(view, "web_search_handler_id"):
                view.disconnect(view.web_search_handler_id)
                del view.web_search_handler_id

    def do_update_state(self):
        pass

    def append_search_to_context_menu(self, view, popup):
        menu_item = Gtk.MenuItem.new_with_label("Web Search")
        menu_item.connect("activate", lambda _: self.search())
        menu_item.show()

        separator = Gtk.SeparatorMenuItem.new()
        separator.show()

        popup.append(separator)
        popup.append(menu_item)

    def get_search_query(self):
        doc = self.view.get_buffer()
        if doc.get_has_selection():
            start, end = doc.get_selection_bounds()
        else:
            start = doc.get_iter_at_mark(doc.get_insert())
            end = start.copy()
            if not start.starts_word() and (start.inside_word() or start.ends_word()):
                start.backward_word_start()

            if not end.ends_word() and end.inside_word():
                end.forward_word_end()

        return doc.get_text(start, end, False)

    def search(self):
        query = self.get_search_query()
        if query:
            settings = Gio.Settings.new(WEB_SEARCH_SCHEMA)
            try:
                url = (
                    (settings.get_default_value("query-url").get_string() % query)
                    if not settings.get_string("query-url")
                    else (settings.get_string("query-url") % query))
            except TypeError:
                return

            if settings.get_boolean("use-custom-browser"):
                try:
                    webbrowser.get(settings.get_string("browser")).open(url)

                    return
                except webbrowser.Error:
                    pass

            webbrowser.open(url)


class WebSearchConfigurable(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = "WebSearchConfigurable"

    def __init__(self):
        super().__init__()

    def do_create_configure_widget(self):
        settings = Gio.Settings.new(WEB_SEARCH_SCHEMA)

        builder = Gtk.Builder.new()
        builder.add_from_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "configurationbox.ui"))

        browser_entry = builder.get_object("browser_entry")
        browser_entry.set_text(settings.get_string("browser"))
        browser_entry.set_sensitive(settings.get_boolean("use-custom-browser"))
        browser_entry.connect("changed", lambda _: settings.set_string("browser", browser_entry.get_text()))

        query_url_entry = builder.get_object("query_url_entry")
        query_url_entry.set_text(settings.get_string("query-url"))
        query_url_entry.connect("changed", lambda _: settings.set_string("query-url", query_url_entry.get_text()))

        custom_browser_check = builder.get_object("custom_browser_check")
        custom_browser_check.set_active(settings.get_boolean("use-custom-browser"))
        custom_browser_check.connect("toggled", lambda b: settings.set_boolean("use-custom-browser", b.get_active()))
        custom_browser_check.connect("toggled", lambda b: browser_entry.set_sensitive(b.get_active()))

        return builder.get_object("configuration_box")
