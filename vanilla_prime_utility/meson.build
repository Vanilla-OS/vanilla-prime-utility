pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'prime_utility')
gnome = import('gnome')

gnome.compile_resources('prime_utility',
  'prime-utility.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'vanilla-prime-utility.in',
  output: 'vanilla-prime-utility',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

subdir('widgets')
subdir('windows')
subdir('utils')

prime_utility_sources = [
  '__init__.py',
  'main.py',
]

install_data(prime_utility_sources, install_dir: moduledir)
