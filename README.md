# csv2wiki: CSV->wiki converter

Open source script to convert rows in a CSV file to pages in a wiki.

[csv2wiki](csv2wiki) requires Python 3.  Right now, only
[MediaWiki](https://mediawiki.org/) is supported, but it would not be
hard to extend it to support other wiki APIs.

Basic usage: 

        $ csv2wiki -c CONFIG [OPTIONS] CSV

Run `python3 ./csv2wiki --help` to see complete usage.  Summary:

You create a config file that is specific to the particular CSV and
destination wiki.  The config file contains various parameters about
the conversion: wiki URL and login information, which columns in the
CSV should be included, a template for naming the resultant wiki
pages, etc.  Then you run the script at the command line, passing the
config file with the -c option and the CSV file as an argument.

A sample of csv2wiki in action (along with a
[config file](https://github.com/OpenTechStrategies/MacFound/blob/master/csv2wiki-config.tmpl)
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

to see usage.  If you run it on the accompanying test data
spreadsheet, [test-input.csv](test-input.csv), for example like this:

        $ ./find-unique-columns -g 2,4 -g 3,4 -g 1,6 -g 2,6 -g 3,6 -g 2,3 -s "-" test-input.csv

You should see output like this:

        Individual columns that are unique across all rows:
        
          1. Identifying Number
          5. Ridiculously Unique Random String
        
        Unique combination: 2-4
        
          2. Not-Quite-Unique Name
          4. Non-Unique Vegetable
        
        Unique combination: 2-3
        
          2. Not-Quite-Unique Name
          3. Non-Unique Animal
        
        Unique combination: 1-6
        
          1. Identifying Number
          6. Something That's The Same In Every Row
    
## Related projects

If you like this, you might also like [csvkit](http://csvkit.rtfd.org/).
