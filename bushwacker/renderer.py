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

import jinja2
from webassets.ext import jinja2 as webassets_jinja2

# Reuse the Jinja2 exception
from jinja2 import TemplateNotFound  # NOQA


class Base(object):
    def __init__(self, config):
        self.config = config

    def __call__(self, template, output_file, context=None):
        raise NotImplementedError("Function render not implemented")


class Jinja2(Base):
    def __init__(self, assets_environment, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        src = os.path.abspath(self.config['src'])
        templates = os.path.abspath(self.config['templates'])

        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(src),
            jinja2.FileSystemLoader(templates),
        ])

        extensions = [webassets_jinja2.AssetsExtension]
        self.environment = jinja2.Environment(loader=loader,
                                              extensions=extensions)
        self.environment.assets_environment = assets_environment

    def __call__(self, template, output_file, context=None):
        if not context:
            context = dict()
        template = self.environment.get_template(template)
        return template.stream(context).dump(output_file)
