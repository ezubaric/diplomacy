import re
import sqlite3
import sys
# from unidecode import unidecode  # pyflakes reports unused
import csv


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
    order = order.strip()
    if any(order.startswith(x) for x in kADJECTIVES):
        country, order = order.split(" ", 1)
    else:
		country = assumed_country

    order = order.strip()
    assert order.startswith("Fleet") or order.startswith("Army"), \
      "Bad start of order: %s" % order
    unit_type, order = order.split(" ", 1)

    if " -> " in order:
        locations = order.split(" -> ")
        # Need to handle arbitrary number of locations because of convoys
        start = locations[0]
        stop = locations[-1]
    else:
        if order.startswith("Army") or order.startswith("Fleet"):
            unit_type, order = order.split(" ", 1)

        if " " in order:
            start, hold = order.split(" ", 1)
        else:
            start = order.strip()
        stop = start

    return country, unit_type, start, stop


def movement_tuples(message, row):
    for line in message.split("\\n"):
        print("Processing: %s" % line)
        if line.strip().startswith("Ownership of supply centers:"):
            break
        if "build pending" in line:
            break
        if ":" in line:
            country, order = line.split(":", 1)
            if not country in kCOUNTRIES:
                print("Skipping %s" % line)
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
                unit = unit.strip()

                assert unit.startswith("Fleet") or unit.startswith("Army"), "Bad start of order: %s" % order
                unit_type, location = unit.split(" ", 1)
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

    with open("movements.csv", 'w') as outfile:
        out = csv.DictWriter(outfile, ["game", "time", "subject", "unit_type",
                                       "start_location", "end_location",
                                       "support_country", "order_type",
                                       "country", "result", "support_type",
                                       "support_start", "support_end"])
        out.writeheader()
        for mm in movement_results_bodies(conn):
            base_row = {}
            base_row["game"] = mm["game"]
            base_row["time"] = mm["time"]
            base_row["subject"] = mm["subject"]
            for rr in movement_tuples(mm["text"], base_row):
                out.writerow(rr)
