""" Remove duplicate presses from CSV dumps """

import unicodecsv
import sys

from glob import glob
try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x: x


for f in tqdm(glob("{}/*".format(sys.argv[1]))):
    rdr = unicodecsv.reader(open(f))
    presses = []
    header = rdr.next()
    for fro, to, mile, time, msg in rdr:
        msg = msg.strip()
        exists = False
        toRemove = []
        for fro_other, to_other, mile_other, time_other, msg_other in presses:
            if fro_other.startswith("Re-") and not fro.startswith("Re-") and msg_other == msg and mile_other == mile:
                toRemove.append([fro_other, to_other, mile_other, time_other, msg_other])
            elif not fro_other.startswith("Re-") and fro.startswith("Re-") and msg_other == msg and mile_other == mile:
                exists = True
                break
            elif (fro_other == fro and to_other == to and 
                mile_other == mile and msg_other == msg):
                exists = True
                break
        for item in toRemove:
            presses.remove(item)
        if not exists:
            presses.append([fro, to, mile, time, msg])
    wtr = unicodecsv.writer(open(f, "wb"), lineterminator="\n")
    wtr.writerow(header)
    for press in presses:
        if press[0].startswith("Re-"):
            press[0] = press[0][3:]
        if press[1].startswith("Re-"):
            press[1] = press[1][3:]
        wtr.writerow(press)
