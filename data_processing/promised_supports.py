# Get promised supports

from __future__ import print_function
import unicodecsv
from glob import glob
import re
from os.path import basename
from collections import Counter

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x

from common import kCOUNTRIES, kADJECTIVES

# get a dict of e.g., {'E': 'England'}
full_country = {country[0]: country for country in kCOUNTRIES}

promised_supports = []

for f in glob("../press_data/*"):
    rdr = unicodecsv.reader(open(f))
    rdr.next()  # discard header
    for fro, to, mile, _, msg in rdr:
        if fro not in full_country.keys() or to == "M" or mile.endswith("X"):
            # discard anonymous presses, presses to master and post-game msgs
            continue

        promises_in_message = []
        for line in msg.split("\n"):
            if line.startswith(full_country[fro]):
                m = re.search("SUPPORT ({})".format("|".join(kADJECTIVES)), line)
                if m:
                    # keep track of who the support is in favour of
                    benefitting_country = m.groups()[0]
                    promises_in_message.append((line, benefitting_country))
        if promises_in_message:
            promised_supports.append((basename(f), mile, fro, to,
                                      promises_in_message))

print("n. messages with promises: ", len(promised_supports))
print("total n. promised supports: ", sum(len(s[-1]) for s in
    promised_supports))

print("distribution of number of recipients per msg. with promises: ",
      Counter([len(to) if to != "all" else 6
               for _, _, _, to, _ in promised_supports]).most_common())

print("Promised supports communicated to country being supported: ",
    sum(benefitting_country[0] in to or to == 'all'
        for _, _, _, to, msgs in promised_supports
        for _, benefitting_country in msgs))


print("Promised supports communicated but NOT to country being supported: ",
    sum(not(benefitting_country[0] in to or to == 'all')
        for _, _, _, to, msgs in promised_supports
        for _, benefitting_country in msgs))

print("turn- and pair-wise promises communicate to country being supported: ",
    sum(len(set(benefitting_country
        for _, benefitting_country in msgs
        if benefitting_country[0] in to or to == 'all'))
        for _, _, _, to, msgs in promised_supports
        ))

