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
        for fro_other, to_other, mile_other, _, msg_other in presses:
            if (fro_other == fro and to_other == to and 
                mile_other == mile and msg_other == msg):
                exists = True
                break
        if not exists:
            presses.append((fro, to, mile, time, msg))
    wtr = unicodecsv.writer(open(f, "wb"), lineterminator="\n")
    wtr.writerow(header)
    wtr.writerows(presses)
