# pluma-plugins

## General Information

A set of plugins for Pluma, the official text editor of the MATE desktop environment.

Currently available plugins:

- **duplicateline** - *Duplicate current line, selected text or lines.*
- **editorconfig** - *Maintain consistent coding style using EditorConfig files.*
- **gitbranchindicator** - *Show the current git branch on status bar.*
- **gotofile** - *Quickly find and open a file.*
- **joinlines** - *Join selected lines.*
- **macro** - *Record and playback a macro.*
- **restoreopenfiles** - *Restore previously open files.*
- **selectline** - *Select current line.*
- **togglepanel** - *Show/hide panels with one click.*
- **websearch** - *Search for word under cursor/selected text on the web.*

Note:
- All plugins require `Pluma =< 1.25.2`.
- The *editorconfig* plugin requires `python3-editorconfig`.
- The *gitbranchindicator* plugin requires `python3-pygit2`.

## Installation

```sh
$ git clone https://github.com/fszymanski/pluma-plugins.git
$ mkdir -p ~/.local/share/pluma/plugins
$ cp -r path/to/plugin ~/.local/share/pluma/plugins/

# If it has a .gschema.xml file
$ mkdir -p ~/.local/share/glib-2.0/schemas
$ cp path/to/gschema ~/.local/share/glib-2.0/schemas/
$ glib-compile-schemas ~/.local/share/glib-2.0/schemas
```
