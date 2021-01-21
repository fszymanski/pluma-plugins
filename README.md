## Installation

```
$ git clone https://github.com/fszymanski/pluma-plugins.git
$ mkdir -p ~/.local/share/pluma/plugins
$ cp -avr path/to/plugin/dir ~/.local/share/pluma/plugins/
[ Only if it has a .gschema.xml file ]
$ mkdir -p ~/.local/share/glib-2.0/schemas
$ cp path/to/.gschema.xml/file ~/.local/share/glib-2.0/schemas/
$ glib-compile-schemas ~/.local/share/glib-2.0/schemas
```
