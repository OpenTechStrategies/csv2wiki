# csv2wiki: CSV->wiki converter

Open source script to convert rows in a CSV file to pages in a wiki.

Right now only [MediaWiki](https://mediawiki.org/) instances are
supported, but it would not be too hard to extend this to support
other wiki APIs.  Currently requires Python 2.7; we may switch to
Python 3.0 later.  Basic usage:

        $ csv2wiki -c CONFIG [OPTIONS] CSV

Run `python ./csv2wiki` to see complete usage.  Summary:

You create a config file that is specific to the particular CSV and
destination wiki.  The config file contains various parameters about
the conversion: wiki URL and login information, which columns in the
CSV should be included, a template for naming the resultant wiki
pages, etc.  Then you run the script at the command line, passing the
config file with the -c option and the CSV file as an argument.

A sample of csv2wiki in action (along with a config file to drive it)
can be found in the
[MacArthur repository](https://github.com/OpenTechStrategies/MacFound).

See the [bug
tracker](https://github.com/OpenTechStrategies/csv2wiki/issues) for
known issues; pull requests are welcome.

csv2wiki is free software, distributed under the [GNU Affero General
Public License version 3](LICENSE.md).

If you like csv2wiki, you might also like [csvkit](http://csvkit.rtfd.org/).
