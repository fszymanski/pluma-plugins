project('quickopen', license: 'GPL-3.0-or-later')

python = import('python')

python3 = python.find_installation('python3')

datadir = get_option('prefix') / get_option('datadir')
pluginsdir = datadir / 'pluma' / 'plugins'
schemasdir = datadir / 'glib-2.0' / 'schemas'
pkgdatadir = pluginsdir / meson.project_name()

conf_data = configuration_data()
conf_data.set('PKG_DATA_DIR', pkgdatadir)

subdir('data')

install_data('quickopen.plugin.desktop.in.in',
             rename: 'quickopen.plugin',
             install_dir: pluginsdir)

configure_file(input: '__init__.py.in',
               output: '__init__.py',
               configuration: conf_data,
               install: true,
               install_dir: pkgdatadir)

run_command(python3, '-m', 'compileall', meson.current_source_dir() / 'src', check: true)
install_subdir('src', install_dir: pkgdatadir, strip_directory : true)
