
import csv
import sys
from collections import defaultdict

kFIELDNAMES = ["start_name", "end_name", "country", "count", "start_freq",
               "all_freq", "start_x", "start_y", "end_x", "end_y"]

class LocationLookup:
    def __init__(self, lookup_file):
        self._locations = {}
        self._type = {}
        self._country = {}
        self._abbrv = {}

        with open(lookup_file) as infile:
            for ii in csv.DictReader(infile):
                self._locations[ii["name"]] = (ii["x"], ii["y"])
                self._type[ii["name"]] = ii["type"].split("(")[0]
                self._country[ii["name"]] = None
                if "(" in ii["type"]:
                    self._country[ii["name"]] = ii["type"].split("(")[1].split(")")[0]

                self._abbrv[ii["name"]] = ii["abbreviation"]

    def coord(self, location):
        location = location.replace("->", "")
        location = location.strip()
        if location in self._locations:
            return self._locations[location]
        else:
            print("Missing '%s'" % location)
            return None

def write_moves(counts, totals, locations, filename):
    country_totals = defaultdict(int)
    for ss, cc in totals:
        country_totals[cc] += totals[(ss, cc)]

    with open("%s.move.csv" % filename, 'w') as outfile:
        out = csv.DictWriter(outfile, kFIELDNAMES)
        out.writeheader()

        row = {}
        for ss, cc, ee in counts:
            row["start_name"] = ss
            row["end_name"] = ee
            row["country"] = cc
            row["count"] = counts[(ss, cc, ee)]
            row["start_freq"] = float(counts[(ss, cc, ee)]) / float(totals[(ss, cc)])
            row["all_freq"] = float(counts[(ss, cc, ee)]) / float(country_totals[cc])
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

    locations = LocationLookup(sys.argv[2])

    with open(sys.argv[1]) as infile:
        for ii in csv.DictReader(infile):
            if ii["order_type"] == "move":
                if locations.coord(ii["start_location"]) and \
                  locations.coord(ii["end_location"]):
                  counts[(ii["start_location"], ii["country"], ii["end_location"])] += 1
                  totals[(ii["start_location"], ii["country"])] += 1

    write_moves(counts, totals, locations, sys.argv[3])
