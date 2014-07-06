import sqlite3
import sys
import unicodecsv
#import data_processing
#from data_processing.
from common import all_gamenames_standard, generate_all_game_presses
#from common import *
import os


if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])
    games = all_gamenames_standard(conn)
    for game in games:
        if game.strip() == "":
            continue
        fname = "./press_data/{}".format(game.replace("/", "-").encode("ascii"))
        with open(fname, "wb") as f:
            writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
            writer.writerow(("sender", "receivers", "milestone", "timestamp",
                "message"))
            empty_game = True
            for sender, receivers, milestone, sent, msg in generate_all_game_presses(conn, game):
                empty_game = False
                writer.writerow((sender, receivers, milestone, sent, msg))
        if empty_game:
            os.remove(fname)
