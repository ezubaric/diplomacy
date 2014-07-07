"""Playground for figuring out regexes to extract human move patterns.

Please try to extend the test strings with as many crazy examples from the data
as we can get.
"""

import re

s = """
A VIE-GAL
A BUD S A RUM
A RUM S A VIE-GAL

A Ser Support A Rum-Bul

f Por s F Spa,
f Spa (sc) s f LYO m WES,   # what does sc mean? only one that breaks for now
f LYO m WES,
f WES m Naf,
f TYS m Tun, &
a Pie s f Mar.
"""  # TODO: get more

territory = "[A-Z][A-Za-z]{2}"  # TODO: refine using list
print re.findall(r"[afAF] {0:}(?:-| m | [sS](?:upport)? [afAF] ){0:}(?:-{0:})?"\
    .format(territory), s)
