#!/usr/bin/python
# -*- coding: utf-8  -*
from __future__ import unicode_literals

import re
import pywikibot

from base_job import Job

site = pywikibot.Site()


class Pui(Job):
    name = 'pui'
    schedule = '@daily'

    def gen(self):
        return [pywikibot.Page(site, 'Wikipedia:Possibly unfree files')]

    def do_page(self, page):
        wikitext = page.get()
        search = re.compile(r'\n==New listings==', re.IGNORECASE)
        wikitext = search.sub(r'\n*[[/{{subst:#time:Y F j|-8 days}}]]\n==New listings==', wikitext)
        EditMsg = 'Adding new day to holding cell'
        page.put(wikitext, EditMsg)

if __name__ == '__main__':
    Pui().run()
