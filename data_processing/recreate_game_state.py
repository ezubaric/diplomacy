from os import listdir
from os.path import basename
import unicodecsv

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

def writeState(phase):
    for country in countries:
        pos = countries.get(country)
        for location in pos:
            for u in unit:
                gswriter.writerow((phase,country,location,u))

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

                updateSC(country, "", location)
                """existingSC = supplycenter.get(country,[])
                existingSC.append(location)
                supplycenter[country] = existingSC"""
        
        gswriter.writerow(("phase","Country","Location","Type"))
        writeState("Beginning")
        
        scwriter.writerow(("phase","Country","Location"))
        writeSC("Beginning")

        for r in reader:
            lines = r[2].split("\n")
            for line in lines:
                if line.count("->")!=0 and line.count("bounce")==0:
                    l = l.split()
                    country = l[0][:-1]
                    unit = l[1]
                    oldlocation = l[2]
                    newlocation = l[3]
                    updateUnit(country, oldlocation, newlocation,unit)
        writeState(r[0])
        

    except UnicodeDecodeError:
        print gamename
        pass
        
        
    
    
    
    
    
