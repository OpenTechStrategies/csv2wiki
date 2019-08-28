#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Convert a CSV file to wiki pages.  Run 'csv2wiki --help' or see
# https://github.com/OpenTechStrategies/csv2wiki for details.
#
# Copyright (C) 2017 Open Tech Strategies, LLC
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

__doc__ = """\
Convert each row of a UTF-8 CSV file to a MediaWiki page.

Basic usage:

  $ python3 -m csv2wiki -c CONFIG_FILE [OPTIONS] CSV_FILE

The common case is to pass a CSV_FILE on the command line; wiki pages
will then be created (or updated) based on the CSV contents.

This script expects the cells in CSV_FILE to contain HTML snippets.
The cells need not be valid HTML documents, but they should be
formatted with balanced HTML tags as opposed to, say, Markdown format.

The CONFIG_FILE contains the wiki URL, login information, and various
other run-time parameters.  It is in standard .ini file format, with
a sole "[default]" section and the following elements in that section:

  wiki_url:            The url of the wiki, e.g. "http://localhost/mediawiki",
                       "https://www.example.com/mwiki", etc.

  username:            User account with write/create permission in the wiki.

  password:            The wiki password corresponding to the username.

  toc_name:            Title for the generated Table of Contents page.

  title_tmpl:          Template into which selected column values from
                       a row are substituted to create the title of
                       each row's page.  Columns are specified with
                       "{N}" in the string, where N is a column number.
                       The special column {0} is the CSV row number,
                       which is automatically left-padded with zeros
                       appropriately for the total number of rows.

                       For example:

                       Suppose title_tmpl is "Entry_{1}_{3}_{0}",
                       column 1 contains "foo", column 3 has "bar",
                       and this is row 15 of a CSV file with 250 rows.
                       The page title corresponding to this row would
                       be "Entry_foo_bar_015".

                       *NOTE:* 

                       The titles generated this way must be unique.
                       There are various ways to ensure uniqueness:

                         - By making sure that at least one element of 
                           title_tmpl comes from a column that holds
                           some kind of unique identifying number;

                         - By making sure that the combination of
                           columns used always results in a unique
                           title;

                         - By interpolating the row number ("{0}"),
                           which is essentially an implicit column
                           that is guaranteed to be unique, although
                           it has no relationship to the data.

                       The 'find-unique-columns' program shipped with
                       csv2wiki can help with the first two methods.

                       If the generated page titles are not unique,
                       only the last row in the set of duplicates will
                       appear in the wiki.  (TODO: we could solve this
                       by checking for collisions and adding a unique
                       tail when one happens, but we currently don't
                       do that.  So, be careful.)

  cat_col:             The number of the column (if any) in the CSV
                       file that should be used to create a category
                       for that row; column numbering begins at 1, not
                       0.  Omit this, or leave the value blank, to not
                       use categories at all.

  sec_map:             A map to reorder/rename/regroup columns into sections.

                       This is a versatile option -- the core of
                       csv2wiki.  Spend some time to get to know it.

                       Each wiki page corresponds to a row in the CSV.
                       The sec_map shows the common structure for the
                       pages: what the section nesting is, and which
                       columns go in which sections in what order.
                       Each line in sec_map has one of two forms:

                         - If it begins with one or more dots ("."),
                           it indicates the start of a new section.
                           The number of dots indicates the nesting
                           level: more dots means deeper subsection.

                           After the dots comes an optional section
                           title.  Any instances of "{N}" (N is an integer)
                           in that title will be replaced with the
                           column heading for column N.  Note this
                           uses 1-based indexing: the first column is
                           column 1, and there is no column 0.

                         - If it begins with a pipe character ("|"),
                           it indidcates a text line where any instance
                           of "{N}" (N is an integer) in that text line
                           will be replaced with the row data for that
                           column.  Any space immediately following
                           the pipe will be removed.

                           If N is also the cat_col, then it will also
                           be a wiki link to the category.

                           csv2wiki used to support sec_map lines that
                           had only integers in them, but in order to
                           fulfill that functionality, you should do:

                           | {N}

                         - If it begins with a pound sign ("#"), it will
                           be discarded from the sec_map as a comment.

                       Here is an example 'sec_map':

                         sec_map:  .   Applicant {1}
                                   # A comment about applicants
                                   | {1}
                                   .   Contents
                                   | __TOC__
                                   .   Proposal
                                   ..  Executive Summary
                                   | {12}
                                   ..  Detailed Proposal
                                   | {15}
                                   .   Organization Info
                                   | Title, First, Last: {21} {19} {20}
                                   # Title
                                   | {21}
                                   # Phone
                                   | {22}
                                   # Email
                                   | {23}
                                   # City
                                   | {29}
                                   # State / Province
                                   | {30}
                                   # Postal Code
                                   | {31}
                                   # Country
                                   | {32}
                                   .       Comments 
                                   # Reviewer CC Comments
                                   | {53}
                                   # Reviewer BB Comments
                                   | {52}
                                   # Reviewer AA Comments
                                   | {51}
                                   .       Total Score
                                   | {40}
                                   ..  Reviewer CC Score
                                   | {43}
                                   ..  Reviewer BB Score
                                   | {42}
                                   ..  Reviewer AA Score
                                   | {41}

                       Assuming that column 1 has the header "Name",
                       the above would produce a wiki page with this
                       section structure:

                         + Applicant Name
                           [content of cell 1]
                         + Contents
                           [Full table of contents here insteat of at top]
                         + Proposal
                           - Executive Summary
                             [content of cell 12]
                           - Detailed Proposal
                             [content of cell 15]
                         + Organization Info
                           Title, First, Last: [contents of cells 21 19 20]
                           [content of cells 19-23 and 29-32]
                         + Comments
                           [content of cells 53, 52, and 51]
                         + Total Score
                           [content of cell 40]
                           - Reviewer CC Score
                             [content of cell 43]
                           - Reviewer BB Score
                             [content of cell 42]
                           - Reviewer AA Score
                             [content of cell 41]

                       You can use this option to omit columns from
                       the conversion entirely.  If you don't list a
                       column, it simply won't be included in a wiki
                       page at all.

                       The column numbers used in the sec_map always
                       refer to the original column numbers in the
                       CSV; the order in which columns are put on the
                       page never affects config file references to
                       column numbers.

  default_cat:         The default category to use for pages that have
                       no category.  This is used only when cat_col is 
                       present *and* there are multiple categories seen
                       (i.e., other pages do have categories, such that
                       there is more than one active category already).
                       The value is a string; in most cases, you will
                       want the value of last_cat to be the same as this.

  last_cat:            The (case-insensitive) name of the category, if
                       any, that should always be listed last in the
                       table of contents, even if that category contains
                       more pages than some other category.  See also
                       default_cat.

  keep_empty:          If present, still create sections for empty
                       cells in the CSV.  If a value is provided, use
                       that value as the content of the section;
                       otherwise, use the empty string.

                       In omitted, then simply don't create a section
                       within a row's page for any column (cell) that
                       has no content; this is the default behavior.

  delimiter:           A single-char delimiter used to separate columns
                       in a CSV row.  If omitted, defaults to ','.

  quotechar:           A single-char quotechar used to wrap contents of
                       a single cell in the CSV file.  If omitted, 
                       defaults to '"'.

  path_to_api:         The API path under the URL; defaults to "/"; see
                       mwclient.readthedocs.io/en/master/user/connecting.html.
                       Note that on Wikipedia.org, this would be "/w/", 
                       but in most non-Wikipedia instances of MediaWiki,
                       the default "/" is more likely.  So if you're using
                       that default, you don't have to specify this at all.

Example config file
-------------------

Here is an example config file:

  [default]
  wiki_url: http://localhost/mediawiki
  username: wikibot
  password: bqaRY76gtXu
  title_tmpl: Entry_{1}
  toc_name: List_of_Entries
  cat_col: 5
  sec_map:  .   Applicant {1}
            | {3}
            .   Executive Summary
            | {12}
            .   Detailed Proposal
            | {15}
            .   Comments
            ..  Reviewer CC Comments
            | {23}
            ..  Reviewer BB Comments
            | {21}
            ..  Reviewer AA Comments
            | {20}
            .   Total Score
            | {30}
            ..  Reviewer CC Score
            | {29}
            ..  Reviewer BB Score
            | {28}
            ..  Reviewer AA Score
            | {27}

The "[default]" section name at the top must be present.  The .ini
format always has sections, and for the sake of forward compatibility
this script requires the one section's name to be "default".

Command-line options:
---------------------

In general, the config file is for run-time configuration that is
likely to be permanent (e.g., used for a production run), and
command-line options are for optional behavior that is likely to vary
from run to run.  The exception to this is the "-c" option, of course,
since it's how the config file is indicated in the first place.

  -c | --config FILE   Use FILE as the run-time job control file;
                       see the "Example config file" section above.

  --null-as-value      When a cell's entire content is the word
                       "null" (matched case-insensitively), then treat
                       the cell as having that literal content,
                       instead of treating the cell as being empty.
                       (The latter is the default because in most CSV
                       files, if a cell just contains the word "null",
                       that's just a kind of conversion error and is
                       really an indication that the cell is empty.)

  --cat-sort=SORT      How to sort categories on the TOC page.  SORT
                       value may be "size" (the default) or "alpha".

                       If "size", categories are sorted first by the
                       number of member pages in that category (see
                       the 'cat_col' config option), and alphabetically
                       within each size group.  

                       If "alpha", then categories are sorted strictly
                       alphabetically, no matter what their size.

                       In either case, if the 'last_cat' config option
                       is used, that category will always be last on
                       the TOC (assuming the category exists at all,
                       i.e, has any member pages), no matter what the
                       category's size or where it sits alphabetically.

  -q | --quiet         Be silent except for error messages.

  --dry-run            Write pages to stdout instead of to the wiki.
                       Consider using -q with this to avoid confusion.

  --pare N             Convert only 1/N of the CSV rows to wiki pages.
                       This is useful for doing test conversions of a
                       large CSV file, when you don't want to convert
                       every row in every run.  The --pare option will
                       convert just 1/N rows, spaced evenly across the
                       CSV file and selected deterministically.

  --show-columns       Just print all the column headers in the CSV
                       (that is, the values in the first row) to
                       stdout, with each column numbered.  

                       This is a convenience option to aid in writing
                       a config file, and if passed, must be the only
                       option, since it just prints information and
                       exits, without creating any wiki pages.

  -h | --help          Show usage message and exit without error.

Dependencies and Troubleshooting
--------------------------------

* This requires the 'bs4', 'mwclient', and 'unidecode' non-core Python
  modules.  If any of them are not present, you should get an error 
  message explaining what to do.

* You may need to convert carriage returns to linefeeds

  If your CSV input file uses only carriage returns (CR) for line
  breaks, then you must convert it to using line feeds (LF).  On
  Unix-like systems, this should work:

    $ tr '\\r' '\\n' < cr-file.csv > lf-file.csv

  Note this should not be necessary if the CSV file is in CRLF format,
  that is, the Microsoft Windows / MS-DOS standard for line endings,
  which uses both characters together at the end of each line.

* If your CSV includes HTML links that embed images or videos, you may
  need to put something like this in MediaWiki's LocalSettings.php:

    # Makes, e.g., "{{#ev:youtube|some_youtube_video_id}}" work,
    # but you'll need to convert HTML links to EmbedVideo syntax.
    # See https://www.mediawiki.org/wiki/Extension:EmbedVideo.
    wfLoadExtension("EmbedVideo");
    
    # Makes HTML <img> tags work directly.
    # See https://www.mediawiki.org/wiki/Manual:$wgAllowImageTag.
    $wgAllowImageTag = true;


* Creating/deleting pages in a wiki multiple times may require running
  
    $ php maintenance/rebuildall.php
  
  in your MediaWiki instance, to link pages to their categories 
  properly.  That script took about 10 minutes to run for a wiki with
  <300 pages, so be prepared to wait.  Also, as of early 2017 on
  Debian GNU/Linux, one of the authors had to run 'sudo apt-get
  install php7.0-mysql' to enable rebuildall.php to work.

  Sources:
  
  - "Categories aren't working."
    https://www.mediawiki.org/wiki/Topic:T6uzpn51mgb8n5sc

  - "Database connection fails."
    https://www.mediawiki.org/wiki/Thread:Project:Support_desk/\\
    MediaWiki_upgrade_fails_with_Database_error/reply

* If you get errors saving some pages, it may be an anti-spam plugin.
  
  If your MediaWiki instance has Extension:SpamBlacklist enabled,
  then you may get errors when trying to create pages that contain
  certain kinds of URLs or email addresses (namely, URLs or email
  addresses that SpamBlacklist thinks look spammy). 
  
  One solution is to just turn off Extension:SpamBlacklist entirely.
  But even if you don't have that kind of administrative access,
  you might still have enough access to *configure* the extension, 
  in which case you can whitelist everything via a catchall regexp.
  Visit one or of of these pages:
  
    https://mywiki.example.com/index.php?title=MediaWiki:Spam-whitelist
    https://mywiki.example.com/index.php?title=MediaWiki:Email-whitelist
  
  You'll see a commented-out explanation of how the whitelist works.
  Just add a line with the regular expression ".*", as in this example:
  
    # External URLs matching this list will *not* be blocked even if they would
    # have been blocked by blacklist entries.
    #
    # Syntax is as follows:
    #   * Everything from a "#" character to the end of the line is a comment
    #   * Every non-blank line is a regex fragment which will only match hosts inside URLs
    .*
  
  That will let you save a page containing any URL.  (Things work
  similarly on the Email-whitelist page).

csv2wiki is free / open source software under the AGPL-3.0 license.
Please run with --version option for details.
"""

import csv
import getopt, sys
import configparser
import re
import warnings

# For exception matching.
import requests

# Handle non-core modules specially.
non_core_import_failures = []
try:
    import mwclient
except ImportError:
    non_core_import_failures.append("mwclient")
try:
    import unidecode
except ImportError:
    non_core_import_failures.append("unidecode")
try:
    from bs4 import BeautifulSoup
except ImportError:
    non_core_import_failures.append("bs4")
if len(non_core_import_failures) > 0:
    sys.stderr.write(
        "ERROR: One or more modules were not available for import.\n")
    sys.stderr.write(
        "       You need to install them by doing something like this:\n")
    sys.stderr.write("\n")
    for mod in non_core_import_failures:
        sys.stderr.write("         $ sudo pip3 install %s\n" % mod)
    sys.exit(1)

# TODO: This function should no longer be necessary.  csv2wiki now
# only supports UTF-8 input, which Python is well-equipped to handle.
# However, if we're going to get rid of this function, we should be
# sure that doing so really makes no difference in the output.
def massage_string(s):
    """Convert non-ASCII string S to nearest lower ASCII equivalent."""
    # TODO: This is really a todo for the unidecode module
    # (https://pypi.python.org/pypi/Unidecode), not us.  The
    # documentation says to just use the unidecode() function as the
    # entry point.  That's an alias for unidecode_expect_ascii(),
    # which should be the right choice when most of your input is the
    # plain ASCII subset of UTF-8, because it tries to decode using an
    # ASCII assumption and then catches the exception and tries again
    # with non-ascii as the assumption in the rare case that the
    # string is not ASCII.
    #
    # However, I think maybe it has a bug with respect to recent
    # Python versions?  It tries to trap the exception by catching
    # 'UnicodeEncodeError', but the error actually thrown is
    # (reasonably enough) 'UnicodeDecodeError'.  So it just propagates
    # that exception up the stack and never makes it to the
    # unidecode_expect_nonascii() call that would have successfully
    # decoded the string.
    # /usr/local/lib/python2.7/dist-packages/unidecode/__init__.py has
    # the details (on my system, at least).
    #
    # Anyway, the solution is to call unidecode_expect_nonascii()
    # directly and not worry that that's slightly slower overall.
    return unidecode.unidecode_expect_nonascii(s)

class WikiSectionSkel():
    """One section (or subsection, etc) of a wiki page.  
    A single page's structure is represented as a list of these.

    Each instance knows what section level it is at, what its title
    is, and what its cell content is.  The order of the instances in
    the list is the order of sections in the page.  

    This corresponds to the 'sec_map' option in the config file."""
    def __init__(self, level, title=None, content_specifiers=None):
        """Create one (sub)section on a wiki page.

        LEVEL is the section level: 1 for a top-level section, 
        2 for a subsection, 3 for a subsubsection, and so on.

        TITLE is the title for the section; it is not wiki-escaped.
        Any occurrence of "{N}" (where N is a number) in the TITLE
        represents the header string for column N, but it is the
        caller's responsibility to perform that substitution.

        CONTENT_SPECIFIERS a list of strings, where each represents
        a portion of content that can replace occurrences of "{N}"
        with the specific cell in the row related to this page."""

        self.level = level
        self.title = title
        # You might have expected the 'columns' argument to default
        # to [] instead of None.  But Python has singleton default
        # arguments (or "mutable default arguments", as described in
        # python-guide-pt-br.readthedocs.io/en/latest/writing/gotchas/)
        # that are defined once when the function is defined.  So, in
        # order not to have every skel accumulate every column, we use
        # the flag value None and then shim [] in as the proper default.
        self.content_specifiers = [] if content_specifiers is None else content_specifiers

    def __str__(self):
        """String representation, normally used only for debugging."""
        dot_pad = "." * self.level
        spc_pad = " " * self.level
        return "" \
            + dot_pad + " section '%s':\n" % self.title  \
            + spc_pad + " level:          %d\n"  % self.level  \
            + spc_pad + " content_specifiers:  %s\n"  % self.content_specifiers


class WikiSession:
    """One session loading a CSV file into a wiki."""
    # This is MediaWiki-specific right now.  We could conditionalize
    # based on a new config parameter 'wiki_type'.  At least the
    # _do_skel(), _make_page(), _save_page(), and methods would
    # need to be updated.
    def __init__(self, config, csv_input, null_as_value, msg_out, dry_run_out):
        """Start a wiki session, taking login parameters from CONFIG and
        column header information (if needed) from CSV_INPUT.

        If NULL_AS_VALUE, then when a CSV cell's entire content is
        (case-insensitively) the word "null", treat the cell as having
        that literal content, instead of treating the cell as empty.

        If MSG_OUT is not None, it is an output file, and progress
        messages will be written to it regarding page creation, 
        TOC creation, and category creation.

        If DRY_RUN_OUT is not None, it is an output file, and wiki
        page content will be written to that file instead of to the
        wiki API (i.e., the wiki will never be touched).  This is
        useful for testing locally before saving pages to a wiki.
        While it is possible for both this and MSG_OUT to be not None,
        that may cause confusing output, so consider passing None for
        MSG_OUT if you use DRY_RUN_OUT.
        """
        self._csv_input          = csv_input
        self._null_as_value      = null_as_value
        self._msg_out            = msg_out
        self._dry_run_out        = dry_run_out
        self._site_conn          = None  # will be a mwclient Site object
        self._wiki_url           = config['wiki_url']
        self._username           = config['username']
        self._password           = config['password']
        self._title_tmpl         = config['title_tmpl']
        self._toc_name           = config['toc_name']
        self._cat_col            = config.get('cat_col', None)
        self._default_cat        = config.get('default_cat', None)
        self._last_cat           = config.get('last_cat', None)
        self._keep_empty         = config.get('keep_empty', False)
        self._path_to_api        = config.get('path_to_api')
        self._section_structure  = []  # A list of WikiSectionSkel objects.
        # This gets inhaled into self._section_structure later:
        sec_map                  = config.get('sec_map', None)
        
        # Category column is either None or a number (not a string).
        if self._cat_col is not None:
            self._cat_col = int(self._cat_col)

        # This maps page titles to True, so this session can remember
        # every page created and thus protect against double creation.
        self._page_titles = {}

        # Map category names to lists, where the elements of each list are
        # the titles of the pages in the corresponding category.  The
        # special category "" is used for pages that have no category.
        # (If categories are not in use at all, or if no pages have a
        # category, then all pages would be listed under "".)
        self._categories = {}
    
        # Determines how many "0"s to prepend to a row number.
        if self._csv_input is not None:
            self._row_num_fmt = "{:0"                                      \
                                + str(len(str(self._csv_input.row_count))) \
                                + "}"

        if self._path_to_api is None:
            self._path_to_api = "/"

        if self._last_cat is not None:
            # It's always used case-insensitively and w/o surrounding spaces
            self._last_cat = self._last_cat.strip().lower()

        self._csv2wiki_url = 'https://github.com/OpenTechStrategies/csv2wiki'

        if sec_map is not None:
            # We need to turn sec_map into self._section_structure.

            # There are two kinds of lines:
            #
            #   1) New section indicator (starts with dots)
            #   2) Text line (starts with a pipe)
            #   3) Comment line (starts with a pound sign)
            #      - This is not handled explicitly here because
            #        it's handled by the python config parser
            #        before we get the sec_map
            #
            # These regexps help us figure out which kind we've got.
            dot_matcher = re.compile("^(\\.+)\\s*(.*)$")
            txt_matcher = re.compile("^\\|\\s*(.*)$")

            # Because of the way Python parses ConfigParser syntax,
            # the format we get the sec_map in is one big string,
            # splittable on line breaks into a list of lines.
            for line in sec_map.splitlines():
                # As usual, I wish Python had Lisp-style 'cond'.
                if dot_matcher.search(line):
                    m = dot_matcher.match(line)
                    self._section_structure.append(
                        WikiSectionSkel(m.group(1).count("."),
                                        m.group(2) or ""))
                elif txt_matcher.search(line):
                    if len(self._section_structure) == 0:
                        self._section_structure.append(WikiSectionSkel(0, ""))
                    m = txt_matcher.match(line)
                    self._section_structure[-1].content_specifiers.append(m.group(1))
                else:
                    raise Exception("ERROR: "
                                    + "invalid line in sec_map:\n" \
                                    + "       '%s'\n" % line)
        else:  # no sec_map provided, so contruct trivial one from headers
            for i in range(1, len(csv_input.headers)):
                self._section_structure.append(
                    WikiSectionSkel(1, "{%d}" % i, (i,)))

        # Connect to the site.
        if self._dry_run_out is None:
            try:
                self._site_conn = mwclient.Site(self._wiki_url.split("://"), path=self._path_to_api)
            except requests.exceptions.HTTPError as err: 
                sys.stderr.write("ERROR: failed to connect to wiki URL '%s'\n" % self._wiki_url)
                sys.stderr.write("       Error details:\n")
                sys.stderr.write("       ('%s')\n" % err)
                sys.exit(1)
        
            try:
                self._site_conn.login(self._username, self._password)
            except mwclient.errors.LoginError as err:
                sys.stderr.write("ERROR: Unable to log in to wiki; "
                                 "check that username and password are correct.\n")
                sys.stderr.write("       Error details:\n")
                sys.stderr.write("       ('%s')\n" % err)
                sys.exit(1)

    def _wiki_escape_page_title(self, s):
        """Return a wiki-escaped version of STRING."""
        # TODO: This is MediaWiki-specific right now.
        #
        # This was originally motivated by the API rejecting a page
        # with a title like "Entry_72_Foo_Bar_]Baz[.".  Eventually, 
        # we implemented the complete MediaWiki page title escaping. 
        #
        # Note that at least in MediaWiki, escaping page content and
        # escaping page names are not exactly the same thing.  See
        # https://www.mediawiki.org/wiki/Manual:PAGENAMEE_encoding
        # for what's illegal in a page name.  That list sort of
        # includes underscore, because underscores are treated as
        # though they are spaces, but we're okay with that, so we
        # don't filter out underscores below.
        #
        # According to a comment originally here, some fields with
        # "#N/A" apparently failed as text in a page, not as page
        # titles.  But the callers were only calling this on page
        # titles, so presumably the fact that we're no longer
        # replacing "/" below couldn't possibly result in any breakage
        # that wasn't happning before anyway... right?
        for c in ["#", "<", ">", "[", "]", "{", "|", "}",]:
            if s.find(c) != -1:
                # Just replace any problematic characters with "-",
                # and hope that still results in unique page titles.
                s = s.replace(c, "-")
        # Did you know that MediaWiki limits page titles to 255 bytes?
        # Not characters, but actual bytes?  And did you know that if
        # you use the API to try to create a page with a title longer
        # than that, the error message *won't say anything about length*, 
        # leaving you to guess what "invalidtitle" and "Bad Title"
        # mean, and causing you to go spelunking through the MediaWiki
        # source code, in particular 'includes/api/ApiBase.php' and
        # 'includes/Title.php', until you finally DuckDuckGoogle in
        # desparation and, by some miracle, manage to stumble across
        # https://www.mediawiki.org/wiki/Page_title_size_limitations?
        while len(bytes(s, "UTF-8")) > 255:
            s = s[:-1]
        return s

    def _maybe_msg(self, msg):
        """Write MSG to self._msg_out, unless the latter is None."""
        if self._msg_out is not None:
            self._msg_out.write(msg)

    def _save_page(self, page_title, text):
        """Make page PAGE_TITLE in this wiki have TEXT,
        with the standard colophon appended."""
        if page_title in self._page_titles:
            raise Exception("ERROR: tried to save page '%s' " % page_title
                            + "a second time")
        self._page_titles[page_title] = True
        # Put a colophon at the end of every page, because users need to
        # know that the page was auto-generated.  For one thing, that
        # might make them think twice about manually editing it, lest
        # their changes be overwritten by a subsequent run of the script.
        colophon = "\n\n"                                           \
                   + '<span style="font-size:75%" >'                \
                   + "'''Colophon:''' This page was generated by "  \
                   + '[' + self._csv2wiki_url + ' csv2wiki]. '       \
                   + 'Manual changes to this page might be '        \
                   + 'overwritten by a subsequent run of csv2wiki.' \
                   + '</span>'                                      \
                   + '\n'
        # The log message (edit message, commit message, whatever): the
        # metadata you record in MediaWiki whenever you submit a change.
        edit_msg = "Page generated by csv2wiki (" + self._csv2wiki_url + ")."

        if self._dry_run_out is None:
            page = self._site_conn.pages[page_title]
            try:
                page.save(text + colophon, edit_msg)
            except mwclient.errors.APIError as e:
                raise Exception("ERROR: unable to write page: '%s'" % e.info)
        else:
            # We don't include the edit_msg in dry-run output, 
            # but we could. 
            self._dry_run_out.write("~" * len(page_title) + "\n") # klugey
            self._dry_run_out.write("%s\n" % page_title)
            self._dry_run_out.write("~" * len(page_title) + "\n") # klugey
            self._dry_run_out.write("\n")
            self._dry_run_out.write("%s\n" % text + colophon)
            # Again, klugey, but we want easy page-boundary visibility.
            self._dry_run_out.write("\n" + "#" * 78 + "\n\n")

    def _do_skel(self, skel, row):
        """Return the text for a given part of a wiki page.
        SKEL is a WikiSectionSkel.
        ROW is one row (a list of cells) from the csv input.
        """
        text = ""

        for content_specifier in skel.content_specifiers:
            text += "\n"
            text += content_specifier.format(*row)
            text += "\n"

        if text == "":
            if len(skel.content_specifiers) == 0:
                # Sections that don't directly include columns don't
                # get the self._keep_empty treatment; instead, they
                # are always included.
                text = "\n"
            elif self._keep_empty is False:
                # Early out: If this section does have columns, but
                # none of those columns had text and run-time config
                # didn't say to keep empty sections, then the section
                # itself shouldn't even be included.
                return ""
            else:
                text = "\n" + self._keep_empty + "\n"

        return ("=" * skel.level)                                  \
            + " " + (skel.title.format(*self._csv_input.headers))  \
            + " " + ("=" * skel.level)                             \
            + text

    def _wikiize_cell(self, cell):
        """Update a CELL to be ready for the wiki.

        Data from the spreadsheet may not be properly ready to land
        on mediawiki.  This is a central place to handle preparing
        and updating those strings.

        This is MediaWiki-specific, but I imagine a future version of
        this might want to override with formatting for other wikis."""

        if cell.lower() == "null" and not self._null_as_value:
            cell = ""
        elif cell != "":
            # Mediawiki doesn't do tbody
            cell = cell.replace("<tbody>", "").replace("</tbody>", "")
            # Make soup
            warnings.filterwarnings(
                "ignore", category=UserWarning, module='bs4')
            soup = BeautifulSoup(cell, "html.parser")
            soup = wikify_anchors(soup)

            cell = str(soup)

        return cell

    def _update_category_cell(self, cell, page_title):
        """Update a CELL to link to the category.

        Adds the page title information, as well as update the categories
        in the overall structure for table of contents later.  This does
        not check if CELL should be the category, and counts on the
        caller to ensure that it is the correct column."""

        cell_esc = self._wiki_escape_page_title(massage_string(cell))
        cell = '[[:Category:' + cell_esc + '|' + cell_esc + ']]\n'
        cell += '[[Category:' + cell_esc + ']]'
        if self._categories.get(cell_esc) is None:
            self._categories[cell_esc] = [page_title]
        else:
            self._categories[cell_esc].append(page_title)

        return cell

    def _make_page(self, row):
        """Build and save a page based on ROW.

        ROW's first element is the row number as a properly padded
        string, e.g., if the csv has >1000 but <10000 rows, and this
        is the third row, then ROW[0] would be "0003".

        ROW's subsequent elements are the cell values from the
        corresponding row in the csv.  In other words, the csv 
        cells are available using 1-based indexing, which matches 
        how the user refers to column numbers in the config file."""
        # Splice any requested columns into the page name.
        page_title = self._title_tmpl.format(*row)
        # The input is UTF-8, but for wiki page names we
        # want to stick to plain old lower ASCII.
        page_title = massage_string(page_title)
        page_title = self._wiki_escape_page_title(page_title)
        
        # Wikimedia will convert &amp; to an ampersand and
        # then consider that ampersand as the start of a new
        # ampersand-encoded special char and then complains
        # about an invalid page title.  We put underscores
        # fore and aft to break up that second special char.
        if re.search(r"&amp;.*;", page_title):
            page_title = page_title.replace("&amp;", "_&amp;_")
            page_title = page_title.replace("&amp;__", "&amp;_")
            page_title = page_title.replace("__&amp;", "_&amp;")
        
        # How many pages have been categorized so far?
        cats_count = sum(len(val) for val in self._categories.values())

        # Crawl down the page skel, appending page content as needed.
        page_text = ""

        # We wikiize the whole row once so sections can reuse
        #
        # We preprocess the whole row unconditionally, without knowing
        # which columns self._section_structure will actually use.
        wikiized_row = [self._wikiize_cell(cell) for cell in row]

        # We categorize the column if the _cat_col is set at all,
        # regardless of whether the column is actually use in the sec_map
        #
        # Since this is where the wiki TOC gets its category information
        # from, we need to do this regardless of whether it appears on the
        # the page, if a cat_col was specified.
        #
        # In the end, it's okay that we calculate those categories
        # unconditionally because a) we won't actually emit them on
        # the regular wiki pages unless that section is used somewhere
        # in self._section_structure and b) we'll check self._cat_col
        # before creating the Category namespace pages, and presumably
        # the user would only set the cat_col config parameter if they
        # were using the column somewhere in the sec_map.
        # 
        # Still, these distant-but-related conditionals are brittle,
        # so this comment is here to help remind us what's going on.
        if self._cat_col is not None:
            wikiized_row[self._cat_col] = \
                self._update_category_cell(wikiized_row[self._cat_col], page_title)

        for skel in self._section_structure:
            page_text += self._do_skel(skel, wikiized_row)

        # If the number of categorized pages didn't change, then
        # this row (page) didn't fall into any named category, so put
        # it in the magical category whose name is the empty string.
        if cats_count == sum(len(val) for val in self._categories.values()):
            if self._categories.get("") is None:
                self._categories[""] = [page_title]
            else:
                self._categories[""].append(page_title)

        self._save_page(page_title, page_text)
        self._maybe_msg(("CREATED PAGE: \"" + page_title + "\"\n"))

    def make_pages(self, pare, cat_sort="size"):
        """Create a wiki page for each row in the csv.
        The csv must have at least one row of content.

        If PARE is not None, it is an integer indicating that only
        1/PARE rows should be handled, and the rest skipped.

        CAT_SORT may be "size" (the default) or "alpha", and controls
        how the categories on the TOC page are sorted; see the
        documentation for the '--cat-sort' option for details.
        """
        # read in csv
        row_num = 0
        for row in self._csv_input:
            row_num += 1
            if pare is not None and row_num % pare != 0:
                continue
            # Prepend the row number as the first element below (as a
            # zero-padded string), so that the user has access to the
            # row number via the special code "{0}" in title_tmpl in
            # the config file, and so that all the remaining columns
            # use 1-based indexing, which matches how the user refers
            # to columns in the config file.
            row_num_str = self._row_num_fmt.format(row_num)
            self._make_page([row_num_str] + row)
    
        # create the TOC page.
        toc_text = ""

        # Remember, there's a magical category whose name is "".
        # Even if we have no other categories, we have that one.
        num_categories = len(list(self._categories.keys()))
    
        # This got too big to fit into a lambda anymore :-).
        def categories_sorter(key):
            """Return a descending sort value for category KEY.
            Works whether ambient cat_sort value is "size" or "alpha".

            If "size", then categories will still be sorted
            alphabetically within the same size.  For example,
            if five categories have size 8 (that is, each of those
            five categories in the TOC lists 8 pages), then those five
            categories will be appear in alphabetical order within
            the group of "all categories of size 8".

            If "alpha", then sort strictly alphabetically, both among
            and within categories.
            """
            # Look, laugh if you want, but it works.
            fmt = "{:015}"
            bounce = 9999999999999
            if (self._last_cat is not None
                and key.strip().lower() == self._last_cat):
                if cat_sort == "size":
                    return fmt.format(bounce)
                else:
                    # This works too.  Stop laughing.
                    return "zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz"
            elif cat_sort == "size":
                num = bounce - len(self._categories[key])
                return fmt.format(num) + key.strip().lower()
            else:
                return key.strip().lower()
        
        if ((num_categories > 1) and (self._categories.get("") is not None)):
            if self._default_cat is not None:
                self._categories[self._default_cat] = self._categories[""]
            else:
                # This is janky, but we have to do something, because
                # the TOC is going to be organized by category, and we
                # don't want some pages to be left out just because
                # they were uncategorized.
                #
                # Furthermore, we can't use "" as a category, because
                # trying to actually create that category would result
                # in an error from the MediaWiki API:
                #
                #   ...
                #   raise mwclient.errors.InvalidPageTitle(info.get('invalidreason'))
                #     mwclient.errors.InvalidPageTitle: \
                #     The requested page title is empty or contains only the name of a namespace.
                #
                # So, as a last resort, we just make something up.
                def_cat = "csv2wiki Miscellaneous Default Category"
                self._categories[def_cat] = self._categories[""]
            del self._categories[""]

        for cat in sorted(list(self._categories.keys()), key=categories_sorter):
            if num_categories > 1:
                usable_cat = cat + " (" + str(len(self._categories[cat])) + ")"
                toc_text += "==== " + usable_cat + " ====\n\n"
            for pnam in sorted(self._categories[cat]):
                toc_text += '* [[' + pnam + ']]\n'
            toc_text += "\n"
        self._save_page(self._toc_name, toc_text)
        self._maybe_msg(("CREATED TOC: \"" + self._toc_name + "\"\n"))
        
        # generate the category pages
        if self._cat_col is not None:
            for category in list(self._categories.keys()):
                # Note that just saving the page here might not
                # instantiate the category page with all of its
                # corresponding categorized pages listed on it.  
                # You may need to run the 'rebuildall.php' script
                # on the MediaWiki instance.  See the csv2wiki help
                # output for more about this.
                self._save_page('Category:' + category, "")
                self._maybe_msg(("CREATED CATEGORY: \"" + category + "\"\n"))
    

class CSVInput():
    """Iterator class encapsulating a CSV file as input."""
    def _count_rows(self):
        """Count rows in the csv file, accounting for the headers"""
        
        self._csv_fh.seek(0)
        row_count = sum(1 for row in self._csv_reader) - 1
        
        # Reset the reader for our callers.
        self._csv_fh.seek(0)
        self._csv_reader = csv.reader(self._csv_fh,
                            delimiter=self._config.get('delimiter', ','),
                            quotechar=self._config.get('quotechar', '"'))
        
        return row_count
    
    def __init__(self, csv_input, config):
        """Prepare CSV_FILE for input, with delimiters from CONFIG.
        CONFIG is a dict returned from parse_config_file(), or else
        it is None, in which case default config values are used."""
        self._csv_reader          = None  # will be csv.reader object
        self.headers             = []     # note: will use 1-based indexing
        self.row_count           = None  # will be num rows not counting header
        
        self._config = config or {}
        try:
            self._csv_fh = open(csv_input)
        except TypeError:
            # EAFP for when a stream is coming in rather than a filename
            self._csv_fh = csv_input
        self._csv_reader = csv.reader(self._csv_fh,
                            delimiter=self._config.get('delimiter', ','),
                            quotechar=self._config.get('quotechar', '"'))       

        # First get a row count, so we can pad the row number later.
        self.row_count = self._count_rows()

        # Set column headers, using 1-based indexing.
        self.headers = [None,] + next(self._csv_reader)
        
    def show_columns(self, out):
        """Print this CSV's column names, numbered, to OUT."""
        fmt = "{:0" + str(len(str(len(self.headers) - 1))) + "}"
        for i in range(1, len(self.headers)):
            out.write("%s) %s\n" % (fmt.format(i), self.headers[i]))

    def __iter__(self):
        """Return the underlying iterator for this CSV's rows."""
        return self._csv_reader

    def __next__(self):
        """Return the next row in this CSV."""
        return next(self._csv_reader)
    
def wikify_anchors(soup):
    """Return new soup with all of SOUP's href-bearing anchors wikified.
    That is, anchors of the form <a href="url">text</a> in SOUP will
    be converted to MediaWiki-style "[url text]".

    SOUP, of course, is beautiful soup, because who has time for ugly
    soup?

    """
    for a in soup.select('a'):
        if 'href' in str(a):
            a.replace_with(
                BeautifulSoup("[{1} {0}]".format(a.text, a['href']), 
                              'html.parser'))
    return soup

def usage(errout=False):
    """Print a message explaining how to use this script.
    Print to stdout, unless ERROUT, in which case print to stderr."""
    out = sys.stderr if errout else sys.stdout
    out.write(__doc__)

def version(errout=False):
    """Print a message explaining how to use this script.
    Print to stdout, unless ERROUT, in which case print to stderr."""
    out = sys.stderr if errout else sys.stdout
    out.write("""csv2wiki version 1.0.0.
    
    Copyright (C) 2017, 2018 Open Tech Strategies, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.\n""")

def config_parser_to_dict(config_parser):
    """Return a dictionary mapping fields provided by CONFIG_PARSER to their values."""
    # Return a newly-created dictionary, rather than the ConfigParser
    # object itself, because we want to avoid callers having to pass
    # the 'default' section name every time they access a field.
    config = {}
    for option in config_parser.options('default'):
        config[option] = config_parser.get('default', option)
    return config

def parse_config_string(config_string):
    """Return a dictionary mapping fields in string CONFIG_STRING to their values."""
    config_parser = configparser.ConfigParser()
    config_parser.read_string(config_string)
    return config_parser_to_dict(config_parser)

def parse_config_file(config_file):
    """Return a dictionary mapping fields in CONFIG_FILE to their values."""
    config_parser = configparser.ConfigParser()
    parsed_files = config_parser.read(config_file)
    # ConfigParser.read() returns the number of files read, and if
    # some of them aren't present, it doesn't raise any exceptions
    # about that, it just moves on to try the next one in the list. 
    # (Yes, one could pass it a list of files instead of a single
    # filename.)  Because of this unusual behavior, explained more in
    # https://docs.python.org/2/library/configparser.html, we can't
    # count on an exception being raised and therefore must manually
    # check the returned list instead.
    if len(parsed_files) == 0:
        raise IOError("failed to read config file '%s'" % config_file)
    elif parsed_files[0] != config_file:
        raise IOError("parsed unexpected config file instead of '%s'" % config_file)
    # We have successfully read the config file, so parse it.
    return config_parser_to_dict(config_parser)


def main():
    """Create wiki pages from a supplied CSV."""
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                                   'hv?qd:c:',
                                   ["help",
                                    "version",
                                    "usage",
                                    "quiet",
                                    "dry-run",
                                    "null-as-value",
                                    "cat-sort=",
                                    "pare=",
                                    "config=",
                                    "show-columns"])
    except getopt.GetoptError as err:
        sys.stderr.write("ERROR: '%s'\n" % err)
        usage(errout=True)
        sys.exit(2)

    csv_in = None
    config = None
    wiki_sess = None
    msg_out = sys.stdout
    dry_run_out = None
    bad_opt_seen = False
    null_as_value = False
    cat_sort = "size"
    pare = None
    show_columns = False
    for o, a in opts:
        if o in ("-h", "-?", "--help", "--usage",):
            usage()
            sys.exit(0)
        elif o in ("-v", "--version",):
            version()
            sys.exit(0)
        elif o in ("-q", "--quiet",):
            msg_out = None
        elif o in ("--dry-run",):
            dry_run_out = sys.stdout
        elif o in ("--null-as-value",):
            null_as_value = True
        elif o in ("--cat-sort",):
            cat_sort = a.lower()
        elif o in ("--pare",):
            pare = int(a)
        elif o in ("--show-columns",):
            show_columns = True
        elif o in ("-c", "--config",):
            config = parse_config_file(a)
        else:
            sys.stderr.write("ERROR: unrecognized option '%s'\n" % o)
            bad_opt_seen = True

    if cat_sort != "size" and cat_sort != "alpha":
        sys.stderr.write('ERROR: "--cat-sort" option takes "size" or "alpha"\n')
        usage(errout=True)
        sys.exit(2)

    if config is None and not show_columns:
        sys.stderr.write("ERROR: missing config file; use -c to supply it\n")
        usage(errout=True)
        sys.exit(2)

    if show_columns and (config or pare):
        sys.stderr.write("ERROR: --show-columns precludes any other options\n")
        usage(errout=True)
        sys.exit(2)

    if bad_opt_seen:
        sys.exit(2)

    if len(args) < 1:
        sys.stderr.write("ERROR: missing CSV_FILE argument\n")
        sys.exit(2)
    elif len(args) > 1:
        sys.stderr.write("ERROR: too many arguments; "
                         "expected only CSV_FILE\n")
        sys.exit(2)
    csv_in = CSVInput(args[0], config)

    if show_columns:
        csv_in.show_columns(sys.stdout)
        sys.exit(0)

    wiki_sess = WikiSession(config, csv_in, null_as_value, msg_out, dry_run_out)

    if len(args) < 1:
        sys.stderr.write("ERROR: missing CSV file argument\n")
        usage(errout=True)
        sys.exit(2)
    elif len(args) > 1:
        sys.stderr.write("ERROR: too many arguments\n")
        usage(errout=True)
        sys.exit(2)
    try:
        wiki_sess.make_pages(pare, cat_sort)
    except IndexError as err:
        sys.stderr.write("ERROR: '%s'\n" % err)
        usage(errout=True)
        sys.exit(1)
