# pluma-plugins

## General Information

A set of plugins for Pluma, the official text editor of the MATE desktop environment.

Currently available plugins:

- **duplicateline** - *Duplicate current line, selected text or lines.*
- **editorconfig** - *Maintain consistent coding style using EditorConfig files.*
- **gitbranchindicator** - *Show the current git branch on status bar.*
- **joinlines** - *Join selected lines.*
- **macro** - *Record and playback a macro.*
- **openuri** - *Opens URI in the user's preferred application.*
- **pastebin** - *Store any text on Pastebin.com for easy sharing.*
- **quickopen** - *Quickly open files. (WORK IN PROGRESS!!!)*
- **restoreopenfiles** - *Restore previously open files.*
- **ripgrep** - *Recursively search the current file/directory for lines matching a pattern.*
- **selectline** - *Select current line.*
- **togglepanel** - *Show/hide panels with one click.*
- **websearch** - *Search for the current word/selection on the web.*

Note:

- All plugins require `Pluma >= 1.25.2`.
- The *editorconfig* plugin requires `python3-editorconfig`.
- The *gitbranchindicator* plugin requires `libgit2-glib, gir1.2-ggit`.
- The *openuri* plugin requires `xdg-open`.
- The *pastebin* plugin requires `python3-requests`.
- The *quickopen* plugin requires `git`.
- The *ripgrep* plugin requires `ripgrep`.

## Installation

```sh
$ git clone https://github.com/fszymanski/pluma-plugins.git
```

Plugins that use [meson](https://mesonbuild.com/):

```sh
$ cd path/to/plugin
$ ./install.sh
```

the remaining rest:

```sh
$ mkdir -p ~/.local/share/pluma/plugins
$ cp -r path/to/plugin ~/.local/share/pluma/plugins/

# If it has a .gschema.xml file
$ mkdir -p ~/.local/share/glib-2.0/schemas
$ cp path/to/gschema ~/.local/share/glib-2.0/schemas/
$ glib-compile-schemas ~/.local/share/glib-2.0/schemas
```
