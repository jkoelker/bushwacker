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


import configparser


BOOLEANS = ('debug',)
RAWS = {'blog': ('post_url',)}


class Config(dict):
    def __init__(self, config_file):
        dict.__init__(self)
        self.config_file = config_file

        kwargs = dict(interpolation=configparser.ExtendedInterpolation())
        self.parser = configparser.ConfigParser(**kwargs)

        with open(config_file) as f:
            self.parser.read_file(f)

        self._make_dict()

    def reload(self):
        self.parser.read(self.config_file)
        self._make_dict()

    def _make_dict(self):
        for section in self.parser:
            self[section] = dict()
            for key in self.parser[section]:
                if key in BOOLEANS:
                    value = self.parser.getboolean(section, key)
                elif section in RAWS and key in RAWS[section]:
                    value = self.parser.get(section, key, raw=True)
                else:
                    value = self.parser.get(section, key)
                self[section][key] = value
