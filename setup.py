#!/usr/bin/env python
import os

from configparser import ConfigParser
from setuptools import setup, find_packages


BUMPVERSION_CFG = '.bumpversion.cfg'


# there's a [bumpversion:file:setup.py] feature in bumpversion, but this makes it so the version string is only hardcoded in one place
def get_package_version():
    """
    Read the .bumpversion.cfg file return
    the current version number listed therein.
    Version number only needs to be maintained
    in the .bumpversion.cfg file.

    :return: current package version
    :rtype: str

    """
    config = ConfigParser()
    config.read(BUMPVERSION_CFG)
    current_version = config.get('bumpversion', 'current_version')
    return current_version


def read_requirements():
    """
    Get application requirements from
    the requirements.txt file.

    :return: portal_ui Python requirements
    :rtype: list

    """
    with open('requirements.txt', 'r') as req:
        requirements = req.readlines()
    install_requires = [r.strip() for r in requirements]
    return install_requires


def read(filepath):
    """
    Read the contents from a file.

    :param str filepath: path to the file to be read
    :return: file contents
    :rtype: str

    """
    with open(filepath, 'r') as f:
        content = f.read()
    return content


def identify_data_files(directory_names):
    """
    Recursively introspect the contents
    of a directory. Once the contents have been
    introspected, generate a list directories and
    sub-directories with their contents as lists.

    :param str directory_name: absolute or relative name to a directory
    :return: all contents of a directory as a list of tuples
    :rtype: list

    """
    directory_data_files = []
    for directory_name in directory_names:
        for root, _, files in os.walk(directory_name):
            pathnames = [os.path.abspath(os.path.join(root, filename)) for filename in files]
            data_file_element = (root, pathnames)
            directory_data_files.append(data_file_element)
    return directory_data_files


setup(
    name='nemi_dj_webapp',
    version=get_package_version(),
    description='National Environmental Methods Index User Interface',
    author='James Kreft, Mary Bucknell, Kathryn Schoephoester, Daniel Naab, Laura De Cicco, Andrew Yan, Matt Myers',
    author_email='jkreft@usgs.gov',
    packages=find_packages('./nemi'),
    package_dir={'': 'nemi'},
    include_package_data=True,
    long_description=read('README.md'),
    install_requires=read_requirements(),
    tests_require=read_requirements(),
    platforms='any',
    test_suite='nose.collector',
    zip_safe=False,
    #py_modules=[],
    data_files=identify_data_files(['static'])
)
