#!/usr/bin/env python

config_fname = "../csv2wiki-config"
sanitized_fname = "../sanitized-100andchangeExport-all-judges.csv"

"""These tests check that csv2wiki is putting the right things in the
mediawiki instance.  If mediawiki isn't up, these tests will fail.

"""

# We named csv2wiki using a dash and left out the .py extension, so
# these next two lines ares basically just a regular old import:
import imp
csv2wiki = imp.load_source('csv2wiki', 'csv2wiki')

import urllib2
from bs4 import BeautifulSoup

mediawiki_url = ""
def get_mediawiki_url():
    # Get wiki access url
    global mediawiki_url
    if not mediawiki_url:
        req = urllib2.urlopen(config['wiki_url'])
        mediawiki_url = '/'.join(req.geturl().split('/')[:-1]) + '/'
    return mediawiki_url

created = False
def create_pages():
    """Do the conversion once and then we can run tests on the results.  Note the pare=1.  There should be a test option for quick vs thorough that adjusts pare."""
    global created
    if not created:
        null_as_value = False
        pare = 1
        config = csv2wiki.parse_config_file(config_fname)
        csv_in = csv2wiki.CSVInput(sanitized_fname, config)
        wiki_sess = csv2wiki.WikiSession(config)
        csv2wiki.create_pages(wiki_sess, csv_in, null_as_value, pare)
    created = True

def fetch_page(name):
    """Pull a page from our mediawiki instance"""
    create_pages()
    return urllib2.urlopen(get_mediawiki_url() + name).read()

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
    global config
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
        print "Trying to fetch " + url
        html = fetch_page(url)
        assert html != ""

        ## test wikify_anchors
        assert not "&lt;a href=" in html
        
        fetched_one = True 
        
    print "If we didn't actually fetch one, the prefix detection for entry items is not finding any entry items, which is a problem."
    assert fetched_one == True
