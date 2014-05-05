#!/usr/bin/env python

from __future__ import unicode_literals

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import time

from werkzeug.contrib import cache


class Job:
    name = 'base'
    schedule = '@daily'

    def __init__(self):
        self._logger = None
        self._cache = None
        self._persistent = None

    @property
    def logger(self):
        if self._logger is None:
            path = os.path.expanduser('~/logs/{0}.log'.format(self.name))
            handler = TimedRotatingFileHandler(path, when='W0', backupCount=20, utc=True)
            handler.setLevel(logging.DEBUG)
            handler.setFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self._logger = logging.getLogger(self.name)
            self._logger.addHandler(handler)
            self._logger.addHandler(logging.StreamHandler())

        return self._logger

    def gen(self):
        """
        Override this with some kind of generator
        that returns Page objects
        """
        return []

    def do_page(self, page):
        """
        Do something here.
        @type page pywikibot.Page
        """
        pass

    @property
    def persistent_cache(self):
        if self._persistent is None:
            self._persistent = cache.FileSystemCache(os.path.expanduser('~/cachedir'),
                                                     default_timeout=365*24*60*60,
                                                     threshold=100000)
        return self._persistent

    @property
    def cache(self):
        if self._cache is None:
            timeout = 365 * 24 * 60 * 60
            if 'INSTANCEPROJECT' in os.environ and os.environ['INSTANCEPROJECT'] == 'tools':
                self._cache = cache.RedisCache(host='tools-redis',
                                               key_prefix='legobot-tools',
                                               default_timeout=timeout)
            else:
                self._cache = cache.SimpleCache(default_timeout=timeout)
        return self._cache

    def start_running(self):
        self.persistent_cache.set(self.name+'-running', True)
        self.logger.debug('Starting...')

    def finish_running(self):
        self.persistent_cache.set(self.name+'-running', False)
        self.persistent_cache.set(self.name+'-lastrun', time.time())
        running = self.persistent_cache.get('running')
        if running and self.name in running:
            running.remove(self.name)
            self.persistent_cache.set('running', running)
        self.logger.debug('Finished...')

    def run(self):
        self.start_running()
        for page in self.gen():
            self.do_page(page)
        self.finish_running()

    @property
    def lastrun(self):
        return self.persistent_cache.get(self.name+'-lastrun')

    @property
    def is_running(self):
        return self.persistent_cache.get(self.name+'-running')
