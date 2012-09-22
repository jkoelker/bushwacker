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

import datetime
import logging
import os
import time

from paste import deploy
from watchdog import events
from watchdog import observers
from watchdog import utils
from watchdog.utils import bricks
import webassets

from bushwacker import config
from bushwacker import renderer
from bushwacker import site
from bushwacker.backports import argparse


def now():
    return datetime.datetime.utcnow()


def make_assets(config):
    load_paths = []
    assets_file = ''
    if 'load_path' in config['webassets']:
        load_path = config['webassets']['load_path']
        load_paths.append(load_path)
        assets_file = os.path.join(load_path, 'assets.yaml')
        del config['webassets']['load_path']

    if 'debug' in config['bushwacker']:
        config['webassets']['debug'] = config['bushwacker']['debug']

    if os.path.exists(assets_file):
        from webassets import loaders
        loader = loaders.YAMLLoader(assets_file)
        assets = loader.load_environment()
        for key, value in config['webassets'].iteritems():
            # NOTE(jkoelker) directory and url only exist if they were
            #                initially passed into __init__
            if key in ('directory', 'url') or hasattr(assets, key):
                setattr(assets, key, value)
    else:
        assets = webassets.Environment(**config['webassets'])

    for load_path in load_paths:
        assets.append_path(load_path)

    return assets


class EventHandler(events.PatternMatchingEventHandler):
    def __init__(self, file_queue, *args, **kwargs):
        events.PatternMatchingEventHandler.__init__(self, *args, **kwargs)
        self._file_queue = file_queue

    def on_any_event(self, event):
        if event.src_path:
            # TODO(jkoelker) This is a dirty hack
            if '.git' not in event.src_path:
                self._file_queue.put(event.src_path)


class Generator(utils.DaemonThread):
    def __init__(self, config, args, file_queue=None):
        # NOTE(jkoelker) A Generator can be either a thread or a callable.
        #                If it is only to be a callable, bypass setting up
        #                thread support.
        if file_queue is not None:
            utils.DaemonThread.__init__(self)
            self._file_queue = file_queue
            self._last_file_time = now()
            self._timeout = 1
            self._regenerate_time = 5
        else:
            object.__init__(self)

        self.config = config
        self.assets = make_assets(self.config)
        self.site = site.Site(self.config,
                              renderer.Jinja2(self.assets,
                                              self.config['bushwacker']))

    def _bundle(self):
        logging.info("Generating Assets")
        for bundle in self.assets:
            bundle.build()

    def _site(self, file_path=None):
        logging.info("Generating site")
        self.site(file_path)

    def _should_regenerate(self):
        elapsed = now() - self._last_file_time
        if elapsed.total_seconds() > self._regenerate_time:
            return True
        return False

    def run(self):
        logging.info("Starting generator thread")
        self._regenerate()
        while self.should_keep_running():
            try:
                file = self._file_queue.get(block=False)
                if self._should_regenerate():
                    try:
                        self._regenerate(file)
                    except Exception:
                        msg = "Error regenerating for file %s" % file
                        logging.exception(msg)

            except bricks.queue.Empty:
                time.sleep(self._timeout)
        # FIXME(jkoelker) paste http seems to call os._exit
        logging.info("Stopping generator thread")

    def _regenerate(self, trigger_path=None):
        if trigger_path:
            logging.info("%s changed" % trigger_path)

        if not trigger_path:
            self._bundle()
            self._site()
            return

        for load_path in self.assets.load_path:
            if load_path in trigger_path:
                self._bundle()
                return

        if self.config['bushwacker']['src'] in trigger_path:
            self._site(trigger_path)
            return

        # NOTE(jkoelker) Failsafe
        self._bundle()
        self._site()

    def __call__(self):
        # NOTE(jkoelker) support regenerating outside of the thread
        self._regenerate()


class Server(object):
    def __init__(self, config, args):
        config_uri = 'config:%s' % config.config_file
        src = config["bushwacker"]["src"]
        dst = config["bushwacker"]["dst"]
        file_queue = bricks.OrderedSetQueue()

        self.generator = Generator(config, args, file_queue)
        self.server = deploy.loadserver(config_uri)
        self.app = deploy.loadapp(config_uri)
        self.observer = observers.Observer()

        ignore_patterns = (os.path.join(dst, '*'), '.*', '*.swp', '*.swx',
                           '*.swpx', '*.*~', '*/4913', '*.ini')
        event_handler = EventHandler(file_queue, ignore_directories=True,
                                     ignore_patterns=ignore_patterns)
        self.observer.schedule(event_handler, src, recursive=True)

    def __call__(self):
        self.generator.start()
        self.observer.start()
        self.server(self.app)
        self.observer.stop()
        self.generator.stop()


def generate(config, args):
    generator = Generator(config, args)
    return generator()


def serve(config, args):
    server = Server(config, args)
    return server()


def main():
    parser = argparse.ArgumentParser(description='A static site generator.')
    subparsers = parser.add_subparsers()

    parser.add_argument('-f', '--config-file', default='./bushwacker.ini',
                        help=('Bushwacker config file '
                              '(default ./bushwacker.ini)'))

    gen = subparsers.add_parser('generate', aliases=('g', 'gen'),
                                help='Generate site.')
    gen.set_defaults(func=generate)

    srv = subparsers.add_parser('serve', aliases=('s', 'srv'),
                                help='Serve and regenerate site')
    srv.add_argument('-r', '--reload', default=False, action='store_true',
                     help="Watch src for changes and regenerate")
    srv.set_defaults(func=serve)

    args = parser.parse_args()

    config_file = os.path.abspath(os.path.expanduser(args.config_file))

    if not hasattr(args, "func"):
        print "A command must be specified..."
        parser.print_help()
        return 3

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    try:
        return args.func(config.Config(config_file), args)
    except IOError:
        print 'Unable to find config file: %s' % config_file
        return 1

    return 99
