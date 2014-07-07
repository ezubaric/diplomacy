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
            game_messages = {}
            for sender, receivers, milestone, sent, msg in generate_all_game_presses(conn, game):
                empty_game = False
                [sender_prev, receivers_prev, milestone_prev, sent_prev] = game_messages.get(msg.strip(),["","","",""])
                if sender_prev == "" or sender_prev.startswith("Re-"):
                    game_messages[msg.strip()] = [sender,receivers,milestone,sent]
            for msg in game_messages:
                metadata = game_messages[msg]
                if metadata[0].startswith("Re-"):
                    metadata[0] = metadata[0][3:]
                if metadata[1].startswith("Re-"):
                    metadata[1] = metadata[1][3:]
                writer.writerow((metadata[0], metadata[1], metadata[2], metadata[3], msg))
        if empty_game:
            os.remove(fname)
