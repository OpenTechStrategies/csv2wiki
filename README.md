# csv2wiki: CSV->wiki converter

[csv2wiki](csv2wiki): An open source program to convert rows in a CSV file to pages in a wiki.

csv2wiki requires Python 3.  So far, only
[MediaWiki](https://mediawiki.org/) (v1.28.2 or later) is supported,
but it would not be hard to extend this to support other wikis.

## Usage

Basic usage from current directory:

        $ python3 -m csv2wiki -c CONFIG_FILE --csv=CSV [OPTIONS]

Or run from a different directory by using PYTHONPATH:

        $ PYTHONPATH=<install_dir> python3 -m csv2wiki ...etc...

You can also just run `csv2wiki`, after installing it as a package:

        $ pip3 install -e .

Do `python3 -m csv2wiki --help` to see complete usage.  Summary:

You create a config file that is specific to the particular CSV and
destination wiki.  The config file contains various parameters about
the conversion: wiki URL and login information, which columns in the
CSV should be included, a template for naming the resultant wiki
pages, etc.  Then you run the script at the command line, passing the
config file with the -c option and the CSV file as an argument.

The main thing to pay attention to is the `sec_map` field in the
config file.  That field's value is essentially a small
domain-specific language
([DSL](https://en.wikipedia.org/wiki/Domain-specific_language)) for
mapping the flat structure of a CSV's columns to the nested structure
of sections, subsections, etc in a wiki page.  The documentation (see
`csv2wiki --help`) for `sec_map` is thorough; we recommend that while
reading it you also have at hand an example value for the field, such
as the one in this
[sample config file](https://github.com/OpenTechStrategies/MacFound/blob/master/macfound-internal-csv2wiki-config.tmpl) in
the
[MacArthur repository](https://github.com/OpenTechStrategies/MacFound).

See the [bug
tracker](https://github.com/OpenTechStrategies/csv2wiki/issues) for
known issues; pull requests are welcome.

csv2wiki is free software, distributed under the [GNU Affero General
Public License version 3](LICENSE.md).

## Helper programs

Accompanying csv2wiki are two helper programs:

1. [find-unique-columns](find-unique-columns) helps you quickly figure
   out which columns (or combinations of columns) offer unique values
   across all rows in the spreadsheet.  Run

           $ python3 find-unique-columns --help

   to see usage.  For example, if you can run it on the accompanying test
   data spreadsheet, [test-input.csv](test-input.csv), like this

           $ python3 find-unique-columns -g 2,4,6 -g 3,4 -g 6,1 -g 2,6 -g 3,6 -g 2,3 -s "-" test-input.csv

   the output will show all individually unique columns, the three unique
   combinations of columns (unique when the separator is included, that
   is) from among the six combinations requested, and the maximum cell
   length found across all rows for each column represented:

           Individual columns that are unique across all rows:
           
             1. (max len:  4) Identifying Number
             5. (max len:  8) Ridiculously Unique Random String
           
           Unique combination: 2-3
           
             2. (max len: 13) Not-Quite-Unique Name
             3. (max len: 15) Non-Unique Animal
           
           Unique combination: 2-4-6
           
             2. (max len: 13) Not-Quite-Unique Name
             4. (max len: 11) Non-Unique Vegetable
             6. (max len: 28) Something That's The Same In Every Row
           
           Unique combination: 6-1
           
             6. (max len: 28) Something That's The Same In Every Row
             1. (max len:  4) Identifying Number
    
2. [mwiki-sak](mwiki-sak) The "MediaWiki Swiss Army Knife".  This
   offers command-line-based programmatic access to MediaWiki (using
   the MediaWiki API).  As of this writing, it offers the ability to
   list all pages in the wiki and to delete pages by name.  Run

           $ python3 mwiki-sak --help

   for more information.

## Related projects

If you like this, you might also like [csvkit](http://csvkit.rtfd.org/) and/or [xsv](https://github.com/BurntSushi/xsv).

For quick exploration of a CSV file, try [csv-scope](https://github.com/OpenTechStrategies/ots-tools/blob/master/csv-scope).

To turn a CSV file into an SQL database, try [csvs-to-sqlite](https://github.com/simonw/csvs-to-sqlite).
