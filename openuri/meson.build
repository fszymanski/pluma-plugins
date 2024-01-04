project('openuri', license: 'GPL-3.0-or-later')

datadir = get_option('prefix') / get_option('datadir')
pluginsdir = datadir / 'pluma' / 'plugins'
pkgdatadir = pluginsdir / meson.project_name()

xdg_open = find_program('xdg-open', required: true)

install_data('openuri.plugin.desktop.in.in',
             rename: 'openuri.plugin',
             install_dir: pkgdatadir)

install_data('openuri.py', install_dir: pkgdatadir)

meson.add_install_script('../build-aux/meson/post_install.py', pkgdatadir)
