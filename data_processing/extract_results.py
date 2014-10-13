import re
import sqlite3
import sys
# from unidecode import unidecode  # pyflakes reports unused
import csv
from dateutil import parser
import warnings
from common import kCOUNTRIES, kADJECTIVES, kGOODVARS, game_to_variant

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
        continue
      current_country = None
      for ii in extract_orders(orders):
        yield {"game": gg, "text": ii, "subject": ss, "time": tt}


def parse_move(order, assumed_country):
    order = order.strip()
    if any(order.startswith(x) for x in kADJECTIVES):
        country, order = order.split(" ", 1)
        country = kADJECTIVES[country]
    else:
		country = assumed_country

    order = order.strip()
    assert order.startswith("Fleet") or order.startswith("Army"), \
      "Bad start of order: %s" % order
    unit_type, order = order.split(" ", 1)  # gets rid of Fleet/Army

    if " -> " in order:
        locations = order.split(" -> ")
        # Need to handle arbitrary number of locations because of convoys
        start = locations[0]
        stop = locations[-1].replace(".", "")
    else:

        if order.startswith("Army") or order.startswith("Fleet"):
            # this should never happen
            print("This should never happen!")
            assert False
            unit_type, order = order.split(" ", 1)

        if "hold" in order.lower():
            start, hold = order.rsplit(" ", 1)
        else:
            start = order.strip()
        stop = start

    return country, unit_type, start, stop


def movement_tuples(message, row, escaped=True):
    row["support_start"] = ""
    row["convoy_start"] = ""
    row["convoy_end"] = ""
    row["support_end"] = ""

    linebreak = "\\n" if escaped else "\n"
    for line in message.split(linebreak):
        # print("Processing: %s" % line)
        if line.strip().startswith("Ownership of supply centers:"):
            break
        if "build pending" in line:
            break
        if ":" in line:
            country, order = line.split(":", 1)
            if not country in kCOUNTRIES:
                # print("Skipping %s" % line)
                continue
            row["country"] = country

            if "(*" in order:
                order, result = order.split("(*")
                result = result.replace("*)", "")
                if result == 'invalid':
                    continue
                row["result"] = result
            else:
                row["result"] = ""

            if " SUPPORT " in order:
                row["order_type"] = "support"
                unit, order = order.split(" SUPPORT ", 1)
                unit = unit.strip()

                if not unit.startswith("Fleet") and not unit.startswith("Army"):
                    warnings.warn("Bad start of order: {}".format(unit))
                    continue

                unit_type, location = unit.split(" ", 1)
                row["unit_type"] = unit_type
                row["start_location"] = location
                row["end_location"] = location
                try:
                    sup_country, sup_type, sup_start, sup_end = \
                        parse_move(order, country)
                except AssertionError as e:
                    warnings.warn("Assertion failed: {} in line {}".format(
                        str(e), line))
                    continue

                row["help_country"] = sup_country
                row["help_type"] = sup_type
                row["support_start"] = sup_start.replace(".", "").strip()
                row["support_end"] = sup_end.replace(".", "").strip()
            elif " CONVOY " in order:
                row["order_type"] = "convoy"
                unit, order = order.split(" CONVOY ", 1)
                unit = unit.strip()

                if not unit.startswith("Fleet") and not unit.startswith("Army"):
                    warnings.warn("Bad start of order: {}".format(unit))
                    continue
                unit_type, location = unit.split(" ", 1)
                row["unit_type"] = unit_type
                row["start_location"] = location
                row["end_location"] = location

                try:
                    transport_country, unit_type, start, end = \
                        parse_move(order, country)
                except AssertionError as e:
                    warnings.warn("Assertion failed: " + str(e))
                    continue
                row["convoy_start"] = start
                row["convoy_end"] = end
                row["help_type"] = unit_type
                row["help_country"] = transport_country
            elif "->" or "HOLD" in order:
                if "->" in order:
                    row["order_type"] = "move"
                else:
                    row["order_type"] = "hold"
                try:
                    move_country, unit_type, start, end = \
                        parse_move(order, country)
                except AssertionError as e:
                    warnings.warn("Assertion failed: " + str(e))
                    continue
                row["unit_type"] = unit_type
                row["start_location"] = start
                row["end_location"] = end
                row["help_country"] = ""
                row["help_type"] = ""
                row["support_start"] = ""
                row["support_end"] = ""
            yield row


if __name__ == "__main__":
    print("Looking for database in %s" % sys.argv[1])
    conn = sqlite3.connect(sys.argv[1])

    variants = game_to_variant(conn)
    print(variants)

    with open("movements.csv", 'w') as outfile:
        out = csv.DictWriter(outfile, ["game", "time", "subject",
                                       "unit_type", "start_location", "end_location", "order_type",
                                       "country", "result", "help_type", "help_country",
                                       "support_start", "support_end", "convoy_start", "convoy_end"])

        out.writeheader()
        moves = movement_results_bodies(conn)
        moves = sorted(moves, key=lambda x: (x["game"],
            parser.parse(x["time"])))
        for mm in moves:
            variant = variants[mm["game"]]
            if not variant in kGOODVARS:
                continue
            # print("VAR: %s" % variants[mm["game"]])
            base_row = {}
            base_row["game"] = mm["game"]
            base_row["time"] = mm["time"]
            base_row["subject"] = mm["subject"]
            try:
                for rr in movement_tuples(mm["text"], base_row):
                    out.writerow(rr)
            except AssertionError as e:
                print(e)
                continue

    print(set(variants.values()))
