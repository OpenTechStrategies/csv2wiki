#!/usr/bin/env python3

"""This is a commandline script that uploads documents to wiki pages.

We assume you have a table of contents that lists all the pages.  You
also have a directory with files whose filenames contain clues as to
which page to attach to.  This script looks at the files, tags them
and affiliates them with pages, then uploads them and links to them
from pages.
"""

import json
import mwclient
import os
import re
import requests
import sys
import time

import config as c

def slurp(fname):
    """Read file and return contents"""
    if not os.path.exists(fname):
        return ""
    with open(fname) as fh:
        return fh.read()

class Session():
    def __init__(self, domain, username, pword, datadir, tags):
        """DATADIR is a path to a directory fill of files to consider uploading

        DOMAIN is the url of the wiki server

        USERNAME is the login username

        PWORD is that USERNAME's password

        TAGS are the tags that we're going to care about.  It should be a subset of the tags in c.tags"""
        self.domain = domain
        self.login(domain, username, pword)
        self.datadir = datadir
        self.tags = tags

    def edit_pages(self):
        """Edit wiki pages to include links to uploaded files.  Don't edit
        pages that already have links."""

        edited = slurp('edited.'+self.domain)
        for idnum in self.files.keys():
            for tag in self.tags:
                if tag in self.files[idnum]:
                    fname = "%s_%s%s" % (idnum, tag, os.path.splitext(self.files[idnum][tag])[1])
                    if fname in edited:
                        continue

                    # If there's no page for these files, skip it
                    if not 'page' in self.files[idnum]:
                        continue

                    # Get page text
                    page_title = self.files[idnum]['page']
                    page = self.site.pages[page_title]

                    # Make text to insert
                    section = c.tags[tag][0]
                    #if tag == 'mou': section='MOU'
                    #if tag == 'team': section='Team Structure'
                    insert = "\n= {0} =\n\n* [[Media:{1}|{0} document]]".format(section, fname)
                    
                    # Don't edit twice
                    if insert in page.text():
                        self.record_edit(fname) # record if we somehow missed recording last time
                        continue

                    # Edit and save page
                    text = page.text().split("\n")
                    text.insert(-3,insert) 
                    page.save("\n".join(text), summary='Added link for %s' % section)

                    # Log edit
                    print("Edited %s to link to %s" % (page_title, fname))
                    self.record_edit(fname)

    def gather_files(self):
        """Gather the MOU and Team files, sort them by review number.  Set
        self.files to a dict with keys that are review numbers that hash to
        dicts whose keys are 'mou' and 'team' that hash to filenames."""

        self.files = {}

        # Compile the regexes
        for tag, v in c.tags.items():
            if type(v[1]) != type(re.compile(' ')):
                v[1] = re.compile(v[1])
                
        for fname in os.listdir(self.datadir):
            for tag, v in c.tags.items():
                regex = v[1]
                m = regex.search(fname)
                if m:
                    idnum = m.groups()[0]
                    if not idnum in self.files:
                        self.files[idnum] = {}
                    self.files[idnum][tag] = fname
                    continue
                    
    def gather_pages(self):
        """Add page titles to the self.files dict so we correlate files and pages.
        
        For each dict keyed by a review number in self.files, add a new key 'page' that
        hashes to the title of the page that corresponds to that review number. """ 

        idnum_regex = re.compile(c.toc_id_regex)
        page = self.site.pages[c.toc]
        for line in page.text().split("\n"):
            if not line.startswith("* [["):
                continue
            m = idnum_regex.search(line)
            assert m != None  # Make sure the regex found an id
            idnum = (m.groups()[0])

            # There are some gaps becuse we removed files that wouldn't upload properly
            if not idnum in self.files:
                continue

            page_title = line[4:-2].replace(' ','_')
            self.files[idnum]['page'] = page_title

    def login(self, domain, username, pword):
        """Login via mwclient"""
        self.site = mwclient.Site(domain,
            path='/mwiki/',
            clients_useragent="upload.py")
        self.site.login(username, pword)
           
    def record(self, entry, record_fname):
        """Record ENTRY as a line in RECORD_FNAME"""
        if entry in slurp(record_fname).split("\n"):
            return

        with open(record_fname, 'a') as fh:
            fh.write("%s\n" % entry)
        
    def record_edit(self, fname):
        """After we edit a page to link to fname, write the fname to disk so we skip it next time.
        
        Note that FNAME here is the name of the remote file on the wiki, not
        the name of the file in the local direcotyr."""

        self.record(fname, 'edited.'+ self.domain)

    def record_upload(self, fname):
        """Write the FNAME of the uploaded file to disk so we skip it next time.

        Note that FNAME here is the name of the file in the local direcotry,
        not the name of the remote file in the wiki."""

        self.record(fname, 'uploaded.'+ self.domain)

    def upload_files(self):
        """At this point, we have for every id a page title and the files to
        upload.  Let's do the uploading."""

        uploaded = slurp("uploaded."+self.domain).split("\n")
        for idnum in self.files.keys():
            for tag in self.tags:
                if tag in self.files[idnum]:
                    fname = self.files[idnum][tag]
                    if fname in uploaded:
                        continue
                    fpath = os.path.join(self.datadir, fname)
                    fh = open(fpath, 'rb')
                    try:
                        r = self.site.upload(fh,
                            filename="%s_%s%s" % (idnum, tag, os.path.splitext(fname)[1]),
                            description=fname,
                            ignore=True)
                    except json.decoder.JSONDecodeError:
                        # Sometimes mediawiki replies with html instead of json *facepalm*
                        print("JSON decode error on %s" % fname)
                        print("Such errors were solved in the past by increasing the max file upload size in php.ini and LocalSettings.php")
                        continue
                    except mwclient.errors.APIError:
                        if fname.endswith("doc") or fname.endswith("docx"):
                            print("Doc file treated as a bad zip: %s" % fname)
                        else:
                            raise
                    if r['result'] == 'Success':
                        print("Uploaded " + fpath)
                        self.record_upload(fname)
                        continue
                    elif r['result'] == 'Warning':
                        # All this warnings stuff was mostly for debugging.  By
                        # setting ignore=True in the upload options, we blow
                        # through the warnings.  Still, they were useful for
                        # helping identify issues with the document set.
                        if 'exists' in r['warnings']:
                            self.record_upload(fname)
                            continue
                        if 'duplicate' in r['warnings']:
                            print("%s is a duplicate of %s" % (fname, r['warnings']['duplicate'][0]))
                            continue
                        if 'duplicate-archive' in r['warnings']:
                            print("%s is a duplicate of %s" % (fname, r['warnings']['duplicate-archive']))
                            continue
                    print(r)
                    print("Exiting")

if __name__ == "__main__":
    for d in c.domains:
        print("Working on %s" % d['domain'])
        session = Session(d['domain'], d['username'], d['password'], c.docdir, d['tags'])
        session.gather_files()
        session.gather_pages()
        session.upload_files()
        session.edit_pages()
    print('done')
