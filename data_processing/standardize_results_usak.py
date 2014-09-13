from __future__ import print_function
import unicodecsv
import re
import sqlite3
from common import game_from_db


good_games = ['ap000017', 'ap000018', 'betrayorbust', 'cavalry', 'malafide',
              'meliora', 'nexxice', 'ns000073', 'ns000074', 'ns000075',
              'ns000076', 'ns000077', 'ns000078', 'ns000079', 'ns000080',
              'ns000081', 'ns000082', 'ns000083', 'ns000084', 'ns000085',
              'ns000086', 'ns000087', 'ns000088', 'phan03', 'rems007n',
              'ripallen', 'serendipity', 'showcase01', 'stormbluff', 'xp000030',
              'xp000031', 'xp000032']

conn = sqlite3.connect("./data/usakpress.db")
cur = conn.cursor()


phase_re = r'[SF]\d{4}[MRBA]X?'  # move, retreat, build, adjust

PATH = "./data_standardized/"

game_statuses = {}
for g in good_games:
    game_starting = None
    results = []
    for time, subject, content, _ in game_from_db(cur, g):
        good_subj = re.match(r'USAK:(.*)(Game Starting|Results)', subject)
        if good_subj:
            game_phase, subject = good_subj.groups()
            if (subject == 'Game Starting' and 'selected as Master' in content):
                game_starting = game_phase, subject, content
            elif (subject == 'Results' and
                  (game_phase, subject, content) not in results):
                results.append((game_phase, subject, content))
    if game_starting:
        results = [game_starting] + results

    with open(PATH + "usak-{}.results".format(g), "wb") as f:
        writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
        writer.writerow(("phase", "subject", "content"))
        for game_phase, subj, msg in results:
            writer.writerow((re.search(phase_re, game_phase).group(0),
                             subj,
                             msg))
