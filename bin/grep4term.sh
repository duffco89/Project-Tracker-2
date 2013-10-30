#! /bin/bash
#script to grep for 'keyword' in pjtk2 and template files
# looks in py and html files in pjtk2 and templates directories
# recursively searches directories
# excludes south migrations directory
# returns color formatted results with line-numbers.

find ./templates ./pjtk2 -type f -not -path "*/oldmigrations*" -name \*.py -o -name \*.html | xargs grep --color -Hn "$1"
