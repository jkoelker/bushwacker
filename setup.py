# -*- coding: utf-8 -*-

# Copyright 2012 Jason Kölker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import setuptools


def read(filename):
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        return open(path).read()
    return ''


VERSION = '0.1'
WEBASSETS_URL = ('https://github.com/miracle2k/webassets/tarball/master'
                 '#egg=webassets-0.8.dev')

setup = dict(
    name='bushwacker',
    version=VERSION,
    description="Static site generator",
    long_description=read('README.rst'),
    classifiers=[],
    keywords='',
    author='Jason Kölker',
    author_email='jason@koelker.net',
    url='http://github.com/jkoelker/bushwacker',
    license='Apache 2.0',
    packages=setuptools.find_packages(exclude=['ez_setup',
                                               'examples',
                                               'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'jinja2',
        'PasteScript',
        'configparser',
        'webassets==0.8.dev',
        'PyYAML',
        'watchdog'
    ],
    dependency_links=[
        WEBASSETS_URL,
    ],
    entry_points={
        'console_scripts': ['bushwacker = bushwacker.main:main'],
        'paste.paster_create_template':
            ['bushwacker = bushwacker.templates:Bushwacker'],
    }
)


setuptools.setup(**setup)
