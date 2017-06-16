#!/usr/bin/env python3
"""

This script is for checking the uploads and looking for duplicate files.
Mediawiki doesn't love it if you have duplicate files, but I relaxed the rules
so duplicates are not a problem for mediawiki.  Some applicants put in multiple
applications and so their team structure document might show up twice.  That's
ok and accepting it is easier than trying to find the dupes and then link them
together somehow.

Still, it is useful to know about duplicate files associated with the same
issue number.  Those can be a problem because they point to problems in the
export that gave us the files.  Or perhaps in how the application was filled
out.  We don't want to publish what we think is a Team Structure document and
have it actually be financial data.

This script just goes through the md5sums and prints entries that have the same
hash and also the same review number.  It expects to find a sorted file of
md5sums and files:

    md5sum ../100andchange_export\ 2/* > checklist.chk
    sort checklist.chk -i checklist.chk
    ./dup.py > dupes

"""
with open("checklist.chk") as fh:
    lines = fh.read().split("\n")

last = ('','__')
for line in lines:
    if not line:
        continue
    chksum, fname = line.split(" ",1)
    undef, undef, fname = fname.split('/')
    if chksum == last[0] and fname.split('__',1)[0] == last[1].split('__',1)[0]:
        print("%s = %s" % (last[1], fname))
    last = (chksum, fname)
