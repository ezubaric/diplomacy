
import re
import sqlite3
import sys
from unidecode import unidecode

kMOVEMENT = re.compile("Movement results")

def extract_orders(body):
  yield body

def movement_results_bodies(conn):
    c = conn.cursor()
    for gg, tt, ss, bb in \
      c.execute('SELECT gamename, sent, subject, body FROM messages where body like "%Movement results for %"'):
      try:
        before, orders = bb.split("Movement results for ")
      except ValueError:
        print "============\n%s\n============" % bb
        break
      current_country = None
      for ii in extract_orders(orders):
        yield {"game": gg, "text": ii, "subject": ss, "time": tt}


if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])

    for mm in movement_results_bodies(conn):
        print(unidecode(mm["text"]))
