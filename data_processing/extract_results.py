
import re
import sqlite3
import sys
from unidecode import unidecode

kMOVEMENT = re.compile("Movement results")
kCOUNTRIES = ["England", "Austria", "Germany", "France", "Russia", "Italy", "Turkey"]
kADJECTIVES = ["English", "Austrian", "German", "French", "Russian", "Italian", "Turkish"]

def extract_orders(body):
  yield body

def movement_results_bodies(conn):
    c = conn.cursor()
    for gg, tt, ss, bb in \
      c.execute('SELECT gamename, sent, subject, body FROM messages where body like "%Movement results for %"'):
      try:
        before, orders = bb.split("Movement results for ")
      except ValueError:
        continue
      current_country = None
      for ii in extract_orders(orders):
        yield {"game": gg, "text": ii, "subject": ss, "time": tt}

def parse_move(order, assumed_country):
	if any(order.startswith(x) for x in kADJECTIVES):
		country, order = order.split(" ", 1)
	else:
		country = assumed_country

	assert order.startswith("Fleet") or order.startswith("Army"), "Bad start of order: %s" % order
	unit_type, order = order.split(" ")

	if " -> " in order:
		start, stop = order.split(" -> ")
	else:
		assert "HOLD" in order, "No hold or movement in %s" % order
		start, hold = order.split(" ")
		stop = start

    return country, unit_type, start, stop

def movement_tuples(message, row):
	for line in message.split("\n"):
		if ":" in line:
			country, order = line.split(":", 1)
			if not country in kCOUNTRIES:
				continue
			row["country"] = country

			if "(*" in order:
				order, result = order.split("(*")
				row["result"] = result
			else:
				row["result"] = ""

			if "SUPPORT" in order:
				row["order_type"] = "SUPPORT"
				unit, order = order.split("SUPPORT", 1)

				assert unit.startswith("Fleet") or order.startswith("Army"), "Bad start of order: %s" % order
				unit_type, location = unit.split(" ")
				row["unit_type"] = unit_type
				row["start_location"] = location
				row["end_location"] = location
                sup_country, sup_type, sup_start, sup_end = \
				  parse_move(order, country)
				row["support_country"] = sup_country
				row["support_type"] = sup_type
				row["support_start"] = sup_start
				row["support_end"] = sup_end
			elif "->" or "HOLD" in order:
				move_country, unit_type, start, end = parse_move(order, country)
				row["unit_type"] = unit_type
				row["start_location"] = start
				row["end_location"] = end
				row["support_country"] = ""
				row["support_type"] = ""
				row["support_start"] = ""
				row["support_end"] = ""
			else:
				continue
			yield row

if __name__ == "__main__":
    conn = sqlite3.connect(sys.argv[1])

    for mm in movement_results_bodies(conn):
		base_row = {}
		base_row["game"] = mm["game"]
		base_row["time"] = mm["time"]
		base_row["subject"] = mm["subject"]
        for rr in movement_tuples(mm["text"]):
			print(rr)
