from __future__ import print_function
import re
import sqlite3
import json
from common import game_from_db


good_games = ['ap000017', 'ap000018', 'betrayorbust', 'cavalry', 'malafide',
              'meliora', 'nexxice', 'ns000073', 'ns000074', 'ns000075',
              'ns000076', 'ns000077', 'ns000078', 'ns000079', 'ns000080',
              'ns000081', 'ns000082', 'ns000083', 'ns000084', 'ns000085',
              'ns000086', 'ns000087', 'ns000088', 'phan03', 'rems007n',
              'ripallen', 'serendipity', 'showcase01', 'stormbluff', 'xp000030',
              'xp000031', 'xp000032']

conn = sqlite3.connect("../data/usakpress.db")
cur = conn.cursor()


phase_re = r'[SF]\d{4}[MRBA]X?'  # move, retreat, build, adjust


game_statuses = {}
for g in good_games:
    statuses = {}
    for time, subject, content, _ in game_from_db(cur, g):
        if "Ownership of supply centers" in content:
            if subject.startswith("Re") or subject.startswith("Rcpt") or 'Press' in subject:
                continue
            phase = re.search(phase_re, subject).group(0)
            status = re.search(r'Ownership of supply centers:\n\n.*\n\n(.*)\n\n',
                               content, re.MULTILINE + re.DOTALL)
            if not status:
                print(subject)
                continue
            status = status.group(1)
            ownership = {}
            for line in status.split("\n"):
                country = line.split()[0]
                country = country[:-1]  # strip colon
                supplies, units, _ = re.findall(r"\d+", line)
                supplies, units = int(supplies), int(units)
                ownership[country] = (supplies, units)
            statuses[phase] = ownership
    game_statuses[g] = statuses

json.dump(game_statuses, open("yearly_statuses.json", "w"))
