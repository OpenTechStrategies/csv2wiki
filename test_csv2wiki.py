#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Tests for csv2wiki.
#
# Copyright (C) 2017, 2018 Open Tech Strategies, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__doc__ = """These tests check that csv2wiki is putting the right things 
in the mediawiki instance.  If mediawiki isn't up, these tests will fail.
"""

config_fname = "../csv2wiki-config"
sanitized_fname = ".../path/to/original_input.csv"

import os
import re

# We named csv2wiki without the .py extension, so these next lines
# are basically just a regular old import:
import imp
if os.path.isdir('csv2wiki'):
    csv2wiki = imp.load_source('csv2wiki', 'csv2wiki/csv2wiki')
else:
    csv2wiki = imp.load_source('csv2wiki', 'csv2wiki')

from bs4 import BeautifulSoup
import contextlib
import os
import urllib.request, urllib.error, urllib.parse

# Change working directory context manager
@contextlib.contextmanager
def cwd(direc):
    curdir= os.getcwd()
    os.chdir(direc)
    try: yield
    finally: os.chdir(curdir)

## Load config file
with cwd(os.path.dirname(os.path.abspath(__file__))):
    config = csv2wiki.parse_config_file(config_fname)

mediawiki_url = ""
def get_mediawiki_url():
    # Get wiki access url
    global mediawiki_url
    if not mediawiki_url:
        req = urllib.request.urlopen(config['wiki_url'])
        mediawiki_url = '/'.join(req.geturl().split('/')[:-1]) + '/'
    return mediawiki_url

created = False
def create_pages():
    """Do the conversion once and then we can run tests on the results.  Note the pare=1.  There should be a test option for quick vs thorough that adjusts pare."""
    global created
    if not created:
        null_as_value = False
        pare = 1
        with cwd(os.path.dirname(os.path.abspath(__file__))):
            config = csv2wiki.parse_config_file(config_fname)
            csv_in = csv2wiki.CSVInput(sanitized_fname, config)
        wiki_sess = csv2wiki.WikiSession(config)
        csv2wiki.create_pages(wiki_sess, csv_in, null_as_value, pare)
    created = True

def fetch_page(name):
    """Pull page named NAME from our mediawiki instance and return it as a
string"""
    create_pages()
    return urllib.request.urlopen(get_mediawiki_url() + name).read().decode("utf-8")

def fetch_entry(num):
    """Given an entry number, fetch it from the mediawiki"""
    toc = BeautifulSoup(fetch_page('Test_TOC'), "html.parser")
    toc.select("<li>")

toc = None
def fetch_toc_soup():
    global toc
    if not toc:
        return BeautifulSoup(fetch_page('Test_TOC'), "html.parser")
    return toc

def test_config_file():
    """Make sure the config file is there and we find an expected field."""
    with cwd(os.path.dirname(os.path.abspath(__file__))):
        config = csv2wiki.parse_config_file(config_fname)
        assert config['wiki_url'] != ""
    
def test_toc():
    """Make sure there is a table of contents."""
    html = fetch_page('Test_TOC')
    assert html != ""
    
def test_categories():
    """Make sure categories got added to the TOC"""
    toc = fetch_toc_soup()
    categories = toc.select("span.mw-headline")
    assert categories != []
    
def test_entries():
    """Make sure there are entries and we can download them."""
    toc = fetch_toc_soup()

    entries = toc.find('div', id='mw-content-text').select("a")
    prefix = '/'+'/'.join(get_mediawiki_url().split('/')[3:])
    if not prefix.endswith('/'):
        prefix += '/'
        

    assert len(entries) > 0

    fetched_one = False
    for e in entries:
        href = e.get('href', "")
        if not href:
            continue
        if not prefix in href:
            continue
        url = "Entry"+href.split("/Entry")[1]
        print("Trying to fetch " + url)
        html = fetch_page(url)
        assert html != ""

        # test wikify_anchors
        if "&lt;a " in html:
            for lt in re.findall(r"&lt;a.*&gt;", html):
                print(lt)
        assert not "&lt;a href=" in html

        # Test for <tbody>
        assert not "&lt;tbody" in html    
        fetched_one = True 
        
    print("If we didn't actually fetch one, the prefix detection for entry items is not finding any entry items, which is a problem.")
    assert fetched_one == True

def test_input_csv():
    """The sanitized csv input shouldn't have any "%lt;a href" anchors in
it."""
    with cwd(os.path.dirname(os.path.abspath(__file__))):
        with open(sanitized_fname) as INF:
            csv = INF.read()
    assert not "&lt;a href" in csv

    
