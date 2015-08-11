#!/usr/bin/env
"""
This is the main scheduler and dispatcher
"""
from __future__ import unicode_literals

import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys
import threading
import time

import crontab
from werkzeug.contrib import cache
from scripts import oldid_ga, pui, scotus

path = os.path.expanduser('~/logs/scheduler.log')
handler = TimedRotatingFileHandler(path, when='W0', backupCount=20, utc=True)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger = logging.getLogger('scheduler')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler(sys.stdout))


class JobThread(threading.Thread):
    def __init__(self, job):
        super(JobThread).__init__()
        self.job = job

    def run(self):
        self.job().run()


bots = [
    oldid_ga.OldidGA,
    pui.Pui,
    scotus.Scotus
]

persistent = cache.FileSystemCache(os.path.expanduser('~/cachedir'),
                                   default_timeout=365*24*60*60,
                                   threshold=100000)


def main():
    jobs = {}
    for job in bots:
        jobs[job.name] = job
    # Do an initial pass
    times = {}
    for job in jobs.values():
        ctab = crontab.CronTab(job.schedule)
        times[time.time()+ctab.next()] = job

    while True:
        minimum = min(list(times))
        logger.debug('Sleeping for %s' % (minimum-time.time()))
        time.sleep(minimum-time.time()+15)
        things_to_queue = []
        for time_val, job in dict(times).iteritems():
            if time_val > time.time():
                logger.debug('Queuing %s' % job.name)
                things_to_queue.append(job)
            del times[time_val]
            ctab = crontab.CronTab(job.schedule)
            times[time.time()+ctab.next()] = job
        running = persistent.get('running') or []
        for job in things_to_queue:
            if not job.name in running:
                logger.debug('Starting a thread for %s' % job.name)
                thread = JobThread(job)
                thread.start()
            else:
                logger.debug('Not starting a new %s - already running' % job.name)


if __name__ == '__main__':
    main()
