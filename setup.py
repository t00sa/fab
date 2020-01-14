import os.path
import setuptools

_here = os.path.dirname(__file__)

with open(os.path.join(_here, 'README.md'), 'r', encoding='utf-8') as handle:
    _long_description = handle.read()

with open(os.path.join(_here, 'source', 'fab', '__init__.py'),
          encoding='utf-8') as handle:
    for line in handle:
        bits = line.split('=', 1)
        if bits[0].strip().lower() == '__version__':
            _version = bits[1].strip()
            break
    else:
        raise RuntimeError('Cannot determine package version.')

setuptools.setup(
    name='sci-fab',
    version=_version,
    author='SciFab Developers',
    author_email='metomi@metoffice.gov.uk',
    description='Build system for scientific software',
    long_description=_long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Metomi/fab',
    package_dir={'': 'source'},
    packages=setuptools.find_packages(where='source'),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License','
        'Operating System :: POSIX',
        'ProgrammingLanguage :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Build Tools'
        ],
    python_requires='>=3.6, <4',
    entry_points={'console_scripts': ['fab=fab.__main__:main']},
    project_urls={
        'Bug reports': 'https://github.com/metomi/fab/issues',
        'Source': 'https://github.com/metomi/fab/'
    }
)
