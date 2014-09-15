from os import listdir
from os.path import basename
import unicodecsv

# add player's unit
def addUnit(country, location, unit):
    existingPositions = countries.get(country,{})
    existingUnit = existingPositions.get(location,[])
    existingUnit.append(unit)
    existingPositions[location] = existingUnit
    countries[country] = existingPositions

# update the position of a player's unit
def updateUnit(country, oldloc, newloc, unit):
    existingPositions = countries.get(country,{})
    
    existingUnit = existingPositions.get(oldloc)
    if unit in existingUnit:
        existingUnit.remove(unit)
    if existingUnit != []:
        existingPositions[oldloc] = existingUnit
    else:
        existingPositions.pop(oldloc)
    
    existingUnit = existingPositions.get(newloc,[])
    existingUnit.append(unit)
    existingPositions[newloc] = existingUnit
    countries[country] = existingPositions

# removes player's unit
def removeUnit(country, location, unit):
    existingPositions = countries.get(country,{})
    existingUnit = existingPositions.get(location)
    existingUnit.remove(unit)
    if existingUnit != []:
        existingPositions[location] = existingUnit
    else:
        existingPositions.pop(location)
    countries[country] = existingPositions    

# write all player's units and locations
def writeState(phase):
    for country in countries:
        pos = countries.get(country)
        for location in pos:
            units = pos[location]
            for u in units:
                gswriter.writerow((phase,country,u,location))

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
    gamename = gamename[:-len(".results")]
    print "Processing ", gamename
    reader = unicodecsv.reader(open(foldername + fname,"rb"), encoding="utf8", lineterminator="\n")
    gswriter = unicodecsv.writer(open(gamestatefolder + gamename + ".gamestate", "wb"), encoding="utf8", lineterminator="\n")
    #scwriter = unicodecsv.writer(open(gamestatefolder + gamename + ".supplycenter", "wb"), encoding="utf8", lineterminator="\n")
    
    # skip header
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
                l = line[:-1].split()
                country = l[0][:-1]
                unit = l[1]
                location = ' '.join(l[2:])
                addUnit(country, location, unit)
                #updateSC(country, "", location)
                """existingSC = supplycenter.get(country,[])
                existingSC.append(location)
                supplycenter[country] = existingSC"""
        
        # save initial state
        gswriter.writerow(("phase","Country","Type","Location"))
        writeState("Beginning")
        
        #scwriter.writerow(("phase","Country","Location"))
        #writeSC("Beginning")

        # For all the steps after the initialization phase
        for r in reader:
            # Results for Movement phase
            if r[1].endswith("M"):
                lines = r[2].split("\n")

                for line in lines:
                    if line.count("CONVOY") > 0 or line.count("SUPPORT") > 0 or line.count("HOLD") > 0:
                        continue
                    
                    if line.count("cut") > 0 or line.count("void") > 0 or line.count("dislodged") > 0 or line.count("bounce") > 0 or line.count("no convoy") > 0:
                        continue

                    # record movement for an army/fleet
                    if line.count("->") == 1:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        newlocation = ' '.join(l[l.index("->")+1:])
                        updateUnit(country, oldlocation, newlocation,unit)
                    
                    # for an army passing through the sea using a fleet
                    if line.count("->") > 1:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        l.reverse()
                        secondarrow = len(l)-l.index("->")
                        l.reverse()
                        newlocation = ' '.join(l[secondarrow:])
                        updateUnit(country, oldlocation, newlocation, unit)
                writeState(r[0])

            # Results for Build phase
            elif r[1].endswith("B"):
                lines = r[2].split("\n")
                for line in lines:
                    if line.count("Builds") != 0:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[3].capitalize()
                        location = (' '.join(l[5:]))
                        addUnit(country, location, unit)
                writeState(r[0])

            # Results for Adjustment phase
            elif r[1].endswith("A"):
                lines = r[2].split("\n")
                for line  in lines:
                    if line.count("Builds") != 0:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[3].capitalize()
                        location = (' '.join(l[5:]))
                        addUnit(country, location, unit)
                    elif line.count("Removes") > 0:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[3].capitalize()
                        location = (' '.join(l[5:]))
                        if location.startswith("the "):
                            location = location[4:]
                        removeUnit(country, location, unit)
                writeState(r[0])

            # Results for Retreat phase
            elif r[1].endswith("R"):
                lines = r[2].split("\n")
                for line in lines:
                    if line.count("destroyed") > 0:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[1]
                        location = ' '.join(l[2:l.index("->")])
                        removeUnit(country, location, unit)
                    elif line.count("DISBAND"):
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[1]
                        location = ' '.join(l[2:l.index("DISBAND")])
                        removeUnit(country, location, unit)
                    elif line.count("->") == 1:
                        l = line[:-1].split()
                        country = l[0][:-1]
                        unit = l[1]
                        oldlocation = ' '.join(l[2:l.index("->")])
                        newlocation = ' '.join(l[l.index("->")+1:])
                        updateUnit(country, oldlocation, newlocation,unit)
                writeState(r[0])

    except UnicodeDecodeError:
        print gamename
        pass
