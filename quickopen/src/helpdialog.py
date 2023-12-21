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
        <td>Ctrl + R</td>
        <td>Show recently opened files. <i>(Default)</i></td>
      </tr>
      <tr>
        <td>Ctrl + F</td>
        <td>Show files from the <i>File Browser Pane</i> plugin root directory.</td>
      </tr>
      <tr>
        <td>Ctrl + D</td>
        <td>Show files from directory of the current active document.</td>
      </tr>
      <tr>
        <td>Ctrl + G</td>
        <td>Show files from <i>git</i> directory of the current active document.</td>
      </tr>
      <tr>
        <td>Ctrl + O</td>
        <td>Show files from directory of the current open documents.</td>
      </tr>
      <tr>
        <td>Ctrl + B</td>
        <td>Show files from the bookmark directories.</td>
      </tr>
    </table>
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
