#!/usr/bin/env python
# -*- coding: utf-8 -

# See https://en.wikipedia.org/w/index.php?title=Wikipedia:Bot_requests&oldid=505208009#Create_a_lot_of_unpunctuated_redirects for details
from __future__ import unicode_literals
import re
import pywikibot
from pywikibot import pagegenerators

from base_job import Job

site = pywikibot.Site()
CASE = re.compile('(.*?)\sv.\s(.*)')
REDIR_TEXT = '#REDIRECT [[%s]]\n{{R from modification}}'


class Scotus(Job):
        
    def process_page(self, page):
        if page.isRedirectPage():
            self.logger.debug('* Skipping [[%s]] since it is a redirect.' % page.title())
            return
        elif page.namespace() != 0:
            self.logger.debug('* Skipping [[:%s]] since it is not in the mainspace.' % page.title())
            return
        if not re.search(CASE, page.title()):
            self.logger.debug('* Error: [[:%s]] did not match the case regex.' % page.title())
            return
        redir_title = page.title().replace(' v. ', ' v ')
        redir = pywikibot.Page(site, redir_title)
        if redir.exists():
            self.logger.debug('* Error: [[:%s]] already exists. Skipping.' % redir.title())
            return
        text = REDIR_TEXT % page.title()
        redir.put_async(text, 'BOT: Creating redirect for alternate punctuation')
        self.logger.debug('* Success: [[:%s]] points to [[:%s]].' % (redir.title(), page.title()))

    def gen(self):
        page = pywikibot.Page(site, 'Category:United States Supreme Court cases')
        category = pywikibot.Category(page)
        return pagegenerators.CategorizedPageGenerator(category, recurse=True)


if __name__ == "__main__":
    Scotus().run()