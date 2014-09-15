from os import listdir
from os.path import basename
import unicodecsv

# update the position of a player's unit
def updateUnit(country, oldloc, newloc, unit):
    existingPositions = countries.get(country,{})
    if oldloc != "":
        existingUnit = existingPositions.get(oldloc,[])
        if unit in existingUnit:
            existingUnit.pop(unit)
        existingPositions[oldloc] = existingUnit
    existingUnit = existingPositions.get(newloc,[])
    existingUnit.append(unit)
    existingPositions[newloc] = existingUnit
    countries[country] = existingPositions

def removeUnit(country, location, unit):
    existingPositions = countries.get(country,{})
    existingUnit = existingPositions.get(location,[])
    existingUnit.pop(unit)
    existingPositions[location] = existingUnit
    countries[country] = existingPositions    

# write all player's units and locations
def writeState(phase):
    for country in countries:
        pos = countries.get(country)
        for location in pos:
            for u in unit:
                gswriter.writerow((phase,country,location,u))

# write all player's supply centers
def writeSC(phase):
    for country in supplycenter:
        scs = supplycenter.get(country)
        for sc in scs:
            scwriter.writerow((phase,country,sc))
        

"""def updateSC(country, oldloc, newloc):
    existingSC = supplycenter.get(country,[])
    if oldloc!="":
        existingSC.pop(oldloc)
    existingSC.append(newloc)
    supplycenter[country] = existingSC"""
    

foldername = "./data_standardized/"
gamestatefolder = "./gamestate/"

for fname in listdir(foldername):
    gamename = basename(fname)
    reader = unicodecsv.reader(open(foldername + fname,"rb"), encoding="utf8", lineterminator="\n")
    gswriter = unicodecsv.writer(open(gamestatefolder + gamename + ".gamestate", "wb"), encoding="utf8", lineterminator="\n")
    #scwriter = unicodecsv.writer(open(gamestatefolder + gamename + ".supplycenter", "wb"), encoding="utf8", lineterminator="\n")

    reader.next()

    try:
        countries = {}
        supplycenter = {}
        r = reader.next()
        if r[1].lower().count("starting") == 0:
            continue
        lines = r[2].split("\n")
        for line in lines:
            if line.count("Army")!=0 or line.count("Fleet")!=0:
                l = line.split()
                country = l[0][:-1]
                unit = l[1]
                location = l[2]
                updateUnit(country, "", location, unit)
                """
                existingPositions = countries.get(country,{})
                existingUnit = existingPositions.get(location,[])
                if unit not in existingUnit:
                    existingUnit.append(unit)
                existingPositions[location] = existingUnit
                countries[country] = existingPositions"""

                #updateSC(country, "", location)
                """existingSC = supplycenter.get(country,[])
                existingSC.append(location)
                supplycenter[country] = existingSC"""
        
        gswriter.writerow(("phase","Country","Location","Type"))
        writeState("Beginning")
        
        scwriter.writerow(("phase","Country","Location"))
        writeSC("Beginning")

        for r in reader:
            # Results for Movement phase
            if r[1].endswith("M"):
                lines = r[2].split("\n")
                for line in lines:
                    # CONVOY?
                    # not a support move
                    if line.count("->")==1 and line.count("bounce")==0 and line.count("dislodged")==0 and line.count("SUPPORT")==0:
                        l = line.split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        newlocation = ' '.join(l[l.index("->")+1:])
                        updateUnit(country, oldlocation, newlocation,unit)
                    if line.count("->")==2 and line.count("bounce")==0 and line.count("dislodged")==0 and line.count("SUPPORT")==0:
                        l = line.split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        secondarrow = l.index("->") + l[l.index("->")+1:].index("->")
                        newlocation = ' '.join(l[secondarrow+1:])
                        updateUnit(country, oldlocation, newlocation, unit)
                    #if army dislodged, cut or void
                        
                    # a support or hold move
                    if line.count("SUPPORT")!=0 or line.count("HOLD")!=0:
                        pass
                writeState(r[0])
            # Results for Build phase
            elif r[1].endswith("B"):
                lines = r[2].split("\n")
                for line in lines:
                    if line.count("Builds")!=0:
                        l = line.split()
                        country = l[0][:-1]
                        unit = l[3].capitalize()
                        location = (' '.join(l[5:]))[:-1]
                        updateUnit(country, '', location, unit)
                writerState(r[0])
            # Results for Adjustment phase
                
            # Results for Retreat phase
            elif r[1].endswith("R"):
                lines = r[2].split("\n")
                for line in lines:
                    if line.count("->") == 1 and line.count("destroyed")==0:
                        l = line.split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        newlocation = ' '.join(l[l.index("->")+1:])
                        updateUnit(country, oldlocation, newlocation,unit)
                writeState(r[0])
    except UnicodeDecodeError:
        print gamename
        pass
