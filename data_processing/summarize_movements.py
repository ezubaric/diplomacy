
import csv
import sys
from collections import defaultdict

kFIELDNAMES = ["start_name", "end_name", "country", "target", "count", "start_freq",
               "all_freq", "start_x", "start_y", "end_x", "end_y"]

class LocationLookup:
    def __init__(self, lookup_file):
        self._locations = {}
        self._type = {}
        self._country = {}
        self._abbrv = {}

        territory_count = defaultdict(int)
        with open(lookup_file) as infile:
            for ii in csv.DictReader(infile):
                name = ii["territory"]
                territory_count[name] += 1
                if name in self._locations:
                    x, y = self._locations[name]
                    x += float(ii["x"])
                    y += float(ii["y"])
                    self._locations[name] = (x, y)
                else:
                    self._locations[name] = (float(ii["x"]), float(ii["y"]))

        for ii in territory_count:
            x, y = self._locations[ii]
            self._locations[ii] =  (x / float(territory_count[ii]),
                                    y / float(territory_count[ii]))

    def coord(self, location):
        location = location.replace("->", "")
        location = location.strip()
        if location in self._locations:
            return self._locations[location]
        else:
            print("Missing '%s'" % location)
            return None

def write_moves(counts, totals, locations, filename, action_type):
    with open("%s.%s.csv" % (filename, action_type), 'w') as outfile:
        out = csv.DictWriter(outfile, kFIELDNAMES)
        out.writeheader()

        row = {}
        for ss, cc, tt, ee in counts:
            assert totals[cc] > 0, "Wrong total for %s: tuple %s" % \
              (cc, str((ss, cc, tt, ee)))
            assert totals[(ss, cc)] > 0, "Wrong total for %s, %s: tuple %s" % \
              (ss, cc, str((ss, cc, tt, ee)))
            row["start_name"] = ss
            row["end_name"] = ee
            row["target"] = tt
            row["country"] = cc
            row["count"] = counts[(ss, cc, tt, ee)]
            row["start_freq"] = float(counts[(ss, cc, tt, ee)]) / float(totals[(ss, cc)])
            row["all_freq"] = float(counts[(ss, cc, tt, ee)]) / float(totals[cc])

            if locations.coord(ss) and locations.coord(ee):
              sx, sy = locations.coord(ss)
              ex, ey = locations.coord(ee)
              row["start_x"] = sx
              row["start_y"] = sy
              row["end_x"] = ex
              row["end_y"] = ey
              out.writerow(row)

if __name__ == "__main__":
    counts = defaultdict(int)
    totals = defaultdict(int)
    supporting_totals = defaultdict(int)
    supports = defaultdict(int)

    locations = LocationLookup(sys.argv[2])

    with open(sys.argv[1]) as infile:
        for ii in csv.DictReader(infile):
            if ii["order_type"] == "move":
                if locations.coord(ii["start_location"]) and \
                  locations.coord(ii["end_location"]):
                  counts[(ii["start_location"], ii["country"], "", ii["end_location"])] += 1
                  totals[(ii["start_location"], ii["country"])] += 1
                  totals[ii["country"]] += 1
            if ii["order_type"] == "support":
                supporting_totals[ii["country"]] += 1
                supporting_totals[(ii["start_location"], ii["country"])] += 1
                supports[(ii["start_location"], ii["country"], ii["help_country"], ii["support_start"])] += 1

    write_moves(counts, totals, locations, sys.argv[3], "move")
    write_moves(supports, supporting_totals, locations, sys.argv[3], "sup")
