from setuptools import setup, find_packages


NAME = 'keckdeimosql'
VERSION = '1.0'
RELEASE = 'dev' not in VERSION
AUTHOR = "mbrodheim"
AUTHOR_EMAIL = "mbrodheim@keck.hawaii.edu"
LICENSE = "BSD 3-Clause"
DESCRIPTION = "Package for running PypeIt's quick look functions for DEIMOS"

# scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
#            if os.path.basename(fname) != 'README.rst']
scripts = []
# Define entry points for command-line scripts
entry_points = {
    'console_scripts': [
        "start_deimos_ql = keckdeimosql.scripts.start_deimosql:main"
    ]}

setup(name=NAME,
      provides=NAME,
      version=VERSION,
      license=LICENSE,
      description=DESCRIPTION,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      packages=find_packages(),
      package_data={'keckdeimosql': ['configs/*.cfg']},
      scripts=scripts,
      entry_points=entry_points,
      install_requires=['pypeit',
                        'keckdrpframework']
    #   python_requires="~=3.7"
      )