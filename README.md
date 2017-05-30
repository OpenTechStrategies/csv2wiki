# csv2wiki: CSV->wiki converter

[csv2wiki](csv2wiki): An open source script to convert rows in a CSV file to pages in a wiki.

csv2wiki requires Python 3.  So far, only
[MediaWiki](https://mediawiki.org/) is supported, but it would not be
hard to extend it to support other wiki APIs.  Basic usage: 

        $ csv2wiki -c CONFIG [OPTIONS] CSV

Run `python3 ./csv2wiki --help` to see complete usage.  Summary:

You create a config file that is specific to the particular CSV and
destination wiki.  The config file contains various parameters about
the conversion: wiki URL and login information, which columns in the
CSV should be included, a template for naming the resultant wiki
pages, etc.  Then you run the script at the command line, passing the
config file with the -c option and the CSV file as an argument.

A sample of csv2wiki in action (along with a
[config file](https://github.com/OpenTechStrategies/MacFound/blob/master/macfound-internal-csv2wiki-config.tmpl)
to drive it) can be found in the
[MacArthur repository](https://github.com/OpenTechStrategies/MacFound).

See the [bug
tracker](https://github.com/OpenTechStrategies/csv2wiki/issues) for
known issues; pull requests are welcome.

csv2wiki is free software, distributed under the [GNU Affero General
Public License version 3](LICENSE.md).

## Helper programs

Accompanying csv2wiki is a helper program,
[find-unique-columns](find-unique-columns), to help you quickly figure
out which columns (or combinations of columns) offer unique values
across all rows in the spreadsheet.  Run

        $ python3 ./find-unique-columns --help

to see usage.  For example, if you can run it on the accompanying test
data spreadsheet, [test-input.csv](test-input.csv) like this

        $ ./find-unique-columns -g 2,4,6 -g 3,4 -g 6,1 -g 2,6 -g 3,6 -g 2,3 -s "-" test-input.csv

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
    
## Related projects

If you like this, you might also like [csvkit](http://csvkit.rtfd.org/).
