import imp
import os
if os.path.isdir('csv2wiki'):
    csv2wiki = imp.load_source('csv2wiki', 'csv2wiki/csv2wiki')

