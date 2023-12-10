project('quickopen', license: 'GPL-3.0-or-later')

py = import('python')

python3 = py.find_installation('python3')

pluma_plugins_data_dir = get_option('prefix') / get_option('datadir') / 'pluma' / 'plugins'
schemas_dir = get_option('prefix') / get_option('datadir') / 'glib-2.0' / 'schemas'

conf_data = configuration_data()
conf_data.set('PLUGIN_DATA_DIR', pluma_plugins_data_dir / meson.project_name())

subdir('data')

install_data('quickopen.plugin.desktop.in.in',
             rename: 'quickopen.plugin',
             install_dir: pluma_plugins_data_dir)

configure_file(input: '__init__.py.in',
               output: '__init__.py',
               configuration: conf_data,
               install: true,
               install_dir:  pluma_plugins_data_dir / meson.project_name())

run_command(python3, '-m', 'compileall', meson.current_source_dir() / 'src', check: true)
install_subdir('src', install_dir: pluma_plugins_data_dir / meson.project_name(), strip_directory : true)
