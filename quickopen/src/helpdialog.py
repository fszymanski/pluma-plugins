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

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")
from gi.repository import Gtk, WebKit2

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
        <td>Ctrl + b</td>
        <td>Show files from <i>File Browser Pane</i> plugin root directory.</td>
      </tr>
      <tr>
        <td>Ctrl + d</td>
        <td>Show files from the directory of currently open documents.</td>
      </tr>
    </table>
    <p>
      <b>Note:</b> Recursively traversing directories containing several thousand of files may take 3-5 seconds.
    </p>
  </body>
</html>
"""


class HelpDialog(Gtk.Dialog):
    __gtype_name__ = "QuickOpenHelpDialog"

    def __init__(self, dialog):
        super().__init__(title="Quick Open Help",
                         parent=dialog,
                         flags=Gtk.DialogFlags.MODAL|Gtk.DialogFlags.DESTROY_WITH_PARENT,
                         default_width=800,
                         default_height=200,
                         buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE))

        help_view = WebKit2.WebView()
        help_view.load_html(HELP_HTML, None)

        scroller = Gtk.ScrolledWindow()
        scroller.add(help_view)

        vbox = self.get_content_area()
        vbox.pack_start(scroller, True, True, 0)

        self.connect("response", lambda *_: self.destroy())

        self.show_all()
