# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2023 Filip Szymański <fszymanski.pl@gmail.com>

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gtk
from gi.repository.WebKit2 import WebView

HELP_HTML = """
<!DOCTYPE html>
<html>
  <head>
    <style>
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
      }
    </style>
  </head>
  <body>
    <table>
      <tr>
        <th>Shortcut Key</th>
        <th>Command</th>
      </tr>
      <tr>
        <td>Ctrl + r</td>
        <td>Show recently opened files. <i>(Default)</i></td>
      </tr>
      <tr>
        <td>Ctrl + f</td>
        <td>Show files from <i>File Browser Pane</i> plugin root directory.</td>
      </tr>
      <tr>
        <td>Ctrl + d</td>
        <td>Show files from directory of currently active document.</td>
      </tr>
      <tr>
        <td>Ctrl + g</td>
        <td>Show files from <i>git</i> directory of currently active document.</td>
      </tr>
      <tr>
        <td>Ctrl + o</td>
        <td>Show files from directory of currently open documents.</td>
      </tr>
      <tr>
        <td>Ctrl + b</td>
        <td>Show files from bookmark directories.</td>
      </tr>
    </table>
    <p>
      <b>Note:</b> Recursively searching through directories containing several thousand of files may take 3-5 seconds.
    </p>
  </body>
</html>
"""


@Gtk.Template(resource_path="/org/mate/pluma/plugins/quickopen/ui/helpdialog.ui")
class HelpDialog(Gtk.Dialog):
    __gtype_name__ = "QuickOpenHelpDialog"

    close_button = Gtk.Template.Child()
    help_view = Gtk.Template.Child()

    def __init__(self, dialog):
        super().__init__(parent=dialog)

        self.help_view.load_html(HELP_HTML, None)

        self.close_button.connect("clicked", lambda *_: self.destroy())

        self.show_all()
