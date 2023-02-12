pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
windowsdir = join_paths(pkgdatadir, 'vanilla_prime_utility/windows')

sources = [
  '__init__.py',
  'main_window.py',
  'installation_window.py',
]

install_data(sources, install_dir: windowsdir)