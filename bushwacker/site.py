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
import logging
import shutil


class Site(object):
    def __init__(self, config, renderer):
        self.config = config
        self.renderer = renderer

        # TODO(jkoelker) Should probably only append / if its a dir, but
        #                why would it not be?
        self.src = os.path.abspath(self.config['bushwacker']['src']) + '/'
        self.dst = os.path.abspath(self.config['bushwacker']['dst']) + '/'

    def _strip_src(self, path):
        return path.split(self.src)[-1]

    def _walk_src(self):
        # TODO(jkoelker) convert this to pathtools
        for dirpath, dirnames, filenames in os.walk(self.src):
            for dir in list(dirnames):
                if dir.startswith(('.', '_')):
                    dirnames.remove(dir)

            dirpath = os.path.abspath(dirpath)

            for file in filenames:
                if (file.startswith(('.', '_')) or
                    file.endswith(('.ini', '.ini_tmpl'))):
                        continue

                file = os.path.join(dirpath, file)
                yield self._strip_src(file)

    def _get_context(self):
        return self.config

    def _render(self):
        context = self._get_context()

        for infile in self._walk_src():
            outfile = os.path.abspath(os.path.join(self.dst, infile))

            if not os.path.exists(os.path.dirname(outfile)):
                os.makedirs(os.path.dirname(outfile))

            logging.info("Rendering %s" % outfile)
            self.renderer(infile, outfile, context)

    def _render_static(self):
        # NOTE(jkoelker) Be lazy. This is only here until webassets
        #                feature/117 is merged and completed
        if os.path.exists(self.config['bushwacker']['static']):
            shutil.rmtree(self.config['bushwacker']['static'])
        shutil.copytree(os.path.join(self.src, '_static'),
                        self.config['bushwacker']['static'])

    def __call__(self, file=None):
        if not file:
            self._render()
            self._render_static()
            return

        # TODO(jkoelker) Support only rendering what changed
        self._render()
        self._render_static()
