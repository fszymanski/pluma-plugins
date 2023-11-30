project('quickopen', license: 'GPL-3.0-or-later')

py = import('python')

python3 = py.find_installation('python3')

conf = configuration_data()
conf.set('PLUMA_PLUGINS_DATA_DIR', get_option('prefix') / get_option('datadir') / 'pluma' / 'plugins')
conf.set('PKG_DATA_DIR', conf.get('PLUMA_PLUGINS_DATA_DIR') / meson.project_name())

subdir('data')

install_data('quickopen.plugin.desktop.in.in', rename: 'quickopen.plugin', install_dir: conf.get('PLUMA_PLUGINS_DATA_DIR'))

configure_file(input: '__init__.py.in',
               output: '__init__.py',
               configuration: conf,
               install: true,
               install_dir: conf.get('PKG_DATA_DIR'))

run_command(python3, '-m', 'compileall', meson.current_source_dir() / 'src', check: true)
install_subdir('src', install_dir: conf.get('PKG_DATA_DIR'))
