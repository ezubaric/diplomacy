# Get promised supports

from __future__ import print_function
from os.path import basename
import sys
import csv
import unicodecsv
from glob import glob
import re
from collections import Counter, defaultdict

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x

from common import kCOUNTRIES, kADJECTIVES

# get a dict of e.g., {'E': 'England'}
full_country = {country[0]: country for country in kCOUNTRIES}

promised_supports = []

for f in glob(sys.argv[1] + "/*"):
    rdr = unicodecsv.reader(open(f))
    rdr.next()  # discard header
    for _, _, fro, to, mile, _, msg in rdr:
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
            game = basename(f).split("-", 1)[1].split(".")[0]
            promised_supports.append((game, mile, fro, to,
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

# Now, let's get actual supports

rdr = csv.DictReader(open("../movements.csv"))
supports = [k for k in rdr
            if k['order_type'] == 'support'
            and k['subject'].startswith("USAK")]

supp_games = defaultdict(lambda: defaultdict(lambda: []))
for k in supports:
    m = re.search("([SF]\d\d\d\d\w\w?) Results", k['subject'])
    if m:
        tup = (k['country'],
               k['support_country'],
               k['support_type'],
               k['support_start'],
               k['support_end'])
        mile = m.groups()[0]
        if tup not in supp_games[k['game']][mile]:
            supp_games[k['game']][mile].append(tup)

print("Total support moves actually executed (including self): ",
      sum (1 for game in supp_games.values() for _ in game.values()))

# How often are promises kept?

truths, lies = [], []
for game, mile, fro, to, promises in promised_supports:
    beneficiaries = set(benef for _, benef in promises
                        if benef[0] in to or to == 'all')  # ignore what the actual move would be
    for ben in beneficiaries:
        # check whether fro really supported ben in the given milestone
        supported = False
        for supp_move in supp_games[game][mile]:
            supporter, supportee = supp_move[0], supp_move[1]
            if supporter.startswith(fro) and supportee == ben:
                supported = True  # fro kept her word!
                break
        tup = (game, mile, fro, ben)
        if supported:
            truths.append(tup)
        else:
            lies.append(tup)

print("Promises kept: ", len(truths))
print("Promises broken: ", len(lies))
