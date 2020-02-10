#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of inenv.
# https://github.com/pnegahdar/inenv

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2015, Parham Negahdar <pnegahdar@gmail.com>

from setuptools import setup, find_packages
from inenv.version import __version__


setup(
    name='inenv',
    version=__version__,
    description='Simple multi virtualenv command runner',
    long_description='''
Simple multi virtualenv command runner
''',
    keywords='venv virtualenv python multivenv',
    author='Parham Negahdar',
    author_email='pnegahdar@gmail.com',
    url='https://github.com/pnegahdar/inenv',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        'atomicwrites>=1.1.5',
        'click>=4.0',
        'virtualenv>=13.0.3,<20.0.0',
    ],
    setup_requires=[
        'pytest-runner',
        'pytest-pylint',
        ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pylint',
        "mock; python_version < '3.4'",
    ],
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            'inenv=inenv.cli:run_cli',
            'inenv_helper=inenv.cli:run_cli',
        ],
    },
)
