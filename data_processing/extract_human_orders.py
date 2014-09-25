"""Playground for figuring out regexes to extract human move patterns.

Please try to extend the test strings with as many crazy examples from the data
as we can get.
"""

from __future__ import print_function
import re
from glob import glob
import csv
import unicodecsv
import sys

# get list of territory abbreviations from Jordan's file
terr_lower = set([row['abbreviation'].split()[0]
                  for row in
                  csv.DictReader(open(sys.argv[2])))
# should point to "/local/diplomacy/code/diplomacy/images/map_locations.csv"

# generate uppercase and titlecase variants: aaa -> (aaa, AAA, Aaa)
territory = list(terr_lower) + [t.upper() for t in terr_lower] + \
        [t[0].upper() + t[1:] for t in terr_lower]

# turn into or-regex plus optional "sc" (I don't know what it means)
territory = r"(?:{})(?:\s*\((?:sc|Sc|SC)\))?".format("|".join(territory))

# regex to match human orders.
# It contains two groups:
#  - one covering the ENTIRE match
#  - one covering the support marker (is an empty string if it's not a support order).
# Therefore you can do:
#   for match, supp in re.findall(order_re, press):
#        if supp:
#            ... consider it a promise or a request

order_re = re.compile(r"""(
    (?:[afAF]\s+)?  # army or fleet
    {0:}            # territory name
    (?:\s+[Hh]olds?|  # hold  (probably incomplete)
       (?:\s*-\s*|  # move denoted by dash
          \s+to\s+| # move denoted by " to "
          \s+m\s+|  # move denoted by " m "
          \s+([sS](?:upport)?)\s+(?:[afAF]\s+)?)  # support order
          {0:}(?:\s*-\s*{0:})?)
)""".format(territory), re.VERBOSE)

# Count messages

if __name__ == '__main__':
    n_with_order, n_with_supp = 0, 0
    for f in glob(sys.argv[1] + "/*"):
        rdr = unicodecsv.reader(open(f))
        rdr.next()  # discard header
        for _, _, fro, to, mile, _, msg in rdr:
            if fro not in ("M", "unknown") and to != "M" and not mile.endswith("X"):
                has_match = False
                has_supp = False
                for line in msg.split("\n"):
                    for match, supp in re.findall(order_re, line):
                        has_match = True
                        if supp:
                            has_supp = True
                        #print(match, "\t|\t", line)
                n_with_order += has_match
                n_with_supp += has_supp

    print("Presses with human written orders: ", n_with_order)
    print("Presses with support orders (subset): ", n_with_supp)
