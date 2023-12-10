gnome = import('gnome')

gnome.compile_resources('quickopen',
                        'quickopen.gresource.xml',
                        gresource_bundle: true,
                        install: true,
                        install_dir: pluma_plugins_data_dir / meson.project_name())

install_data('org.mate.pluma.plugins.quickopen.gschema.xml.in',
             rename: 'org.mate.pluma.plugins.quickopen.gschema.xml',
             install_dir: schemas_dir)

gnome.post_install(glib_compile_schemas: true)
