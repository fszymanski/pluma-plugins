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
