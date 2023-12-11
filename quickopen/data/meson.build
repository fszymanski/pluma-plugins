gnome = import('gnome')

gnome.compile_resources('quickopen',
                        'quickopen.gresource.xml',
                        gresource_bundle: true,
                        install: true,
                        install_dir: pkgdatadir)

install_data('org.mate.pluma.plugins.quickopen.gschema.xml.in',
             rename: 'org.mate.pluma.plugins.quickopen.gschema.xml',
             install_dir: schemasdir)

gnome.post_install(glib_compile_schemas: true)
