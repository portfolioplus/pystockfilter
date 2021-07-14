#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" pystockfilter

 Copyright 2019 Slash Gordon

 Use of this source code is governed by a GNU General Public License v3 or
 later that can be
 found in the LICENSE file.
"""

from setuptools import setup, find_packages

EXCLUDE_FROM_PACKAGES = ['test', 'test.*', 'test*']
VERSION = '1.0.8'

with open('README.md', 'r') as fh:
    long_description = fh.read()

INSTALL_REQUIRES = (
    [
        'pystockdb>=1.0.11',
        'cython==0.29.24',
        'python-dateutil==2.8.1',
        'numpy==1.20.3',
        'tulipy==0.4.0'
    ]
)

setup(
    name='pystockfilter',
    version=VERSION,
    author='Slash Gordon',
    author_email='slash.gordon.dev@gmail.com',
    package_dir={'': 'src'},
    description='Financial technical and fundamental analysis indicator'
                ' library for pystockdb.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/portfolioplus/pystockfilter',
    install_requires=INSTALL_REQUIRES,
    packages=find_packages('src', exclude=EXCLUDE_FROM_PACKAGES),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Investment',
    ],
)
