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
        fname = "./data_standardized/usak-{}.press".format(game.replace("/", "-").encode("ascii"))
        with open(fname, "wb") as f:
            writer = unicodecsv.writer(f, encoding="utf8", lineterminator="\n")
            writer.writerow(("actual_sender",
                             "actual_receivers",
                             "apparent_sender",
                             "apparent_receivers",
                             "phase",
                             "timestamp",
                             "message"))
            empty_game = True
            game_messages = {}

            for (sender, receivers, phase, sent,
                 msg) in generate_all_game_presses(conn, game):
                empty_game = False
                writer.writerow((None, None, sender, receivers, phase, sent,
                                 msg.strip()))
        if empty_game:
            os.remove(fname)
