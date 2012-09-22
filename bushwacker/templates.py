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

from paste.util import template
from paste.script import templates


class Bushwacker(templates.Template):
    _template_dir = 'templates'
    summary = "Package with distribute and buildout support"
    vars = [
        templates.var('url', 'URL of homepage'),
    ]

    @staticmethod
    def template_renderer(*args, **kwargs):
        return template.paste_script_template_renderer(*args, **kwargs)

    def pre(self, command, output_dir, vars):
        output_dir = os.path.abspath(os.path.expanduser(output_dir))
        vars['output_dir'] = output_dir
