
import csv

kFIELDNAMES = ["start_name", "end_name", "country", "count", "freq", "percent", "start_coord", "end_coord"]

class LocationLookup:
    def __init__(self, lookup_file):
        self._locations = {}
        self._type = {}
        self._country = {}
        self._abbrv = {}
        
        with open(lookup_file) as infile:
            for ii in DictReader(infile):
                self._locations[ii["name"]] = (ii["x"], ii["y"])
                self._type[ii["name"]] = ii["type"].split("(")[0]
                self._country[ii["name"]] = None
                if "(" in ii["type"]:
                    self._country[ii["name"]] = ii["type"].split("(")[1].split(")")[0]

                self._abbrv[ii["name"]] = ii["abbreviation"]
                

if __name__ == "__main__":
    counts = defaultdict(int)
    totals = defaultdict(int)
    with open("movements.csv") as infile:
        for ii in DictReader(infile):
            if ii["order_type"] == "move":
                counts[(ii["start_location"], ii["country"], ii["end_location"])] += 1
                totals[(ii["start_location"], ii["country"])] += 1
            
    
