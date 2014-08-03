from setuptools import setup
from Cython.Build import cythonize

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

def get_version():
    with open("elevation/__init__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line[15:-2]
    raise Exception("Could not find version number")

setup(
    name="Elevation", # TODO
    version=get_version(),
    author='Cambridge University Spaceflight',
    author_email='contact@cusf.co.uk',
    packages=['elevation'],
    entry_points={
        "console_scripts": [
            # TODO "tawhiri-download = tawhiri.downloader:main"
        ]
    },
    ext_modules = cythonize("elevation/*.pyx"),
    url='http://www.cusf.co.uk/wiki/tawhiri:start',
    license='GPLv3+',
    description='Ground Elevation',
    long_description=long_description,
    install_requires=[
        "Cython==0.20.1",
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering',
    ],
)
