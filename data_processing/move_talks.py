# Get promised supports

from os.path import basename, splitext
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

from common import kCOUNTRIES, kADJECTIVES, get_location_aliases
from recreate_game_state import getGameState

full_country = {country[0]: country for country in kCOUNTRIES}

alias, locations = get_location_aliases()

promised_supports = []

for f in glob(sys.argv[1] + "/*.press"):
    gamename = basename(f)
    gamename, _ = splitext(gamename)
    print "\n\nProcessing ", gamename

    rdr = unicodecsv.reader(open(f))
    rdr.next()  # discard header
    for _, _, fro, to, mile, _, msg in rdr:
        #if fro not in full_country.keys() or to == "M" or mile.endswith("X"):
        if fro == "Master" or to == "Master" or fro == "?" or mile.endswith("X"):
            # discard anonymous presses, presses to master and post-game msgs
            continue

        x = re.compile(r"({0})(\s+)([sS](upport)?)(\s+)(({1})(\s+))?((a|army|f|fleet)(\s+))?({0})[\b(\s+)]".format("|".join([loc.lower() for loc in locations]), "|".join([adj.lower() for adj in kADJECTIVES.keys()])))
        for p in re.finditer(x, msg.lower()):
            print gamename, mile, fro, to, p.group()
            print getGameState(gamename, mile)
        continue
