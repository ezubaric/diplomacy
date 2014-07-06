import sqlite3
import sys
import csv
import data_processing
from data_processing.common import all_gamenames_standard, generate_game_presses
import codecs

if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])

    games = all_gamenames_standard(conn)
    for game in games:
        if game.strip() == "":
            continue
        f = codecs.open(("./press_data/" + game.replace('/','-')).encode("ascii"),"w",encoding='utf8')
        f.write("sender,receivers,milestone,timestamp,message\n");
        for sender, receivers, milestone, sent, msg in generate_game_presses(conn, game):
            f.write(sender + "," + receivers + "," + milestone + "," +  sent + "," + msg.strip() + "\n")
        f.close()
