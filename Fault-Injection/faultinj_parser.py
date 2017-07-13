#!/usr/bin/env python3
import os
import re
import csv
import sys
from collections import Counter

varSDCList = list()
varCrashList = list()
flipList = list()
faultModeList = list()
faultModeSDCList = list()
faultModeCrashList = list()

timeFrameList = list()
timeFrameSDCList = list()
timeFrameCrashList = list()

flipCount = 0
sdcCount = 0
crashCount = 0
sdcCrashCount = 0

sdcFilename = "sdc.csv"
crashFilename = "crash.csv"
summFilename = "summary.csv"

def processDirectory(dirName, fileList):
    flipInfo = ""
    flip=False
    sdc=0
    crash=0
    var = ""
    varFile = ""
    varLine = ""
    initFaultTime = ""
    endFaultTime = ""
    faultMode = ""
    logedFileName = dirName
    for fname in fileList:
        #if re.search("mic\d.log",fname):
        if re.search("\d\d\d\d_\d\d_\d\d_\d\d_\d\d_\d\d_.*.log",fname):
            (sdc, crash) = getSDCCrashInfo(dirName, fname)
            logedName = dirName+"/"+fname
        if re.search("flip_value.*.log",fname):
            (flip, flipInfo, var, varFile, varLine, initFaultTime, endFaultTime, faultMode) = getFlipInfo(dirName, fname)
    if flip:
        #print ("Fault Mode: "+faultMode+"\n")
        global flipCount
        global sdcCount
        global crashCount
        global sdcCrashCount
        if var != "":
            flipCount += 1
            varInfo = var+";"+varFile+";"+str(varLine)
            flipList.append(varInfo)
            faultModeList.append(faultMode)
            timeFrameList.append(initFaultTime+"-"+endFaultTime)
            if sdc == 1:
                faultModeSDCList.append(faultMode)
                timeFrameSDCList.append(initFaultTime+"-"+endFaultTime)
                sdcCount += 1
                varSDCList.append(varInfo)
                csvWFP = open(csvName+"_"+sdcFilename, "a")
                writer = csv.writer(csvWFP, delimiter=';')
                writer.writerow([var,varFile,str(varLine),str(initFaultTime),str(endFaultTime),str(faultMode),logedName])
                csvWFP.close()
            if crash == 1:
                faultModeCrashList.append(faultMode)
                timeFrameCrashList.append(initFaultTime+"-"+endFaultTime)
                crashCount += 1
                varCrashList.append(varInfo)
                csvWFP = open(csvName+"_"+crashFilename, "a")
                writer = csv.writer(csvWFP, delimiter=';')
                writer.writerow([var,varFile,str(varLine),str(initFaultTime),str(endFaultTime),str(faultMode),logedName])
                csvWFP.close()
            if sdc == 1 and crash == 1:
                sdcCrashCount += 1


def getSDCCrashInfo(dirName, fname):
    fp = open(dirName+"/"+fname, "r", errors="replace")
    content = fp.read()
    sdc = 0
    crash = 1
    if re.search("SDC", content):
        sdc = 1
    if re.search("END", content):
        crash = 0
    return (sdc, crash)

def getFlipInfo(dirName, fname):
    fp = open(dirName+"/"+fname, "r", errors="ignore")
    content = fp.read()
    flip = False
    if re.search("Fault Injection Successful",content):
        flip = True
    if flip:
        fp.seek(0)
        btC = False
        bt = ""
        symbolName = ""
        symbolFilename = ""
        symbolLine = 0
        initFaultTime = ""
        endFaultTime = ""
        faultMode = "Single bit-flip"
        for line in fp:
            if re.search("Backtrace BEGIN:",line):
                bt = "Backtrace BEGIN:\n"
                btC = True
            if re.search("Backtrace END", line):
                btC = False
                bt += "Backtrace END\n"
            if btC:
                bt += line
            m = re.match(".*(Memory content before bitflip:.*)",line)
            if m:
                bt += m.group(1)
            m = re.match(".*(Memory content after  bitflip:.*)",line)
            if m:
                bt += m.group(1)
            m = re.match(".*(frame name:.*)",line)
            if m:
                bt += m.group(1)
            m = re.match(".*(symbol name: )(.*)",line)
            if m:
                bt += m.group(1)+m.group(2)
                symbolName = m.group(2)
            m = re.match(".*(symbol filename: )(.*)",line)
            if m:
                bt += m.group(1)+m.group(2)
                symbolFilename = m.group(2)
            m = re.match(".*(symbol line: )(.*)",line)
            if m:
                bt += m.group(1)+m.group(2)
                symbolLine = m.group(2)

            #2017-01-23 15:54:59:initSignal:2
            #2017-01-23 15:54:59:endSignal:4
            m = re.match(".*(initSignal:)(\d+)",line)
            if m:
                bt += m.group(1)+m.group(2)+"s"
                initFaultTime = m.group(2)
            m = re.match(".*(endSignal:)(\d+)",line)
            if m:
                bt += m.group(1)+m.group(2)+"s"
                endFaultTime = m.group(2)

            m = re.match(".*(Fault Mode:)(.*)",line)
            if m:
                bt += m.group(1)+m.group(2)
                faultMode = m.group(2).strip()
                


        return (flip, bt, symbolName, symbolFilename, symbolLine, initFaultTime, endFaultTime, faultMode)
    else:
        return (flip, "", "", "", "", "", "", "")



if len(sys.argv) < 3:
    print ("must set one or more folders to evaluate and a csv name preffix:")
    print (sys.argv[0]+" <folder1> [<folder2> ... <folderN>] <csvFileName>")
    sys.exit(1)

folders = sys.argv[1:-1]
csvName = sys.argv[-1]
print ("Folders: ",folders)
print ("csv Name: ",csvName)


csvWFP = open(csvName+"_"+sdcFilename, "w")
writer = csv.writer(csvWFP, delimiter=';')
writer.writerow(["Variable Name","Variable File","Variable Line", "Init Fault Time", "End Fault Time", "Fault Mode", "dirName"])
csvWFP.close()
csvWFP = open(csvName+"_"+crashFilename, "w")
writer = csv.writer(csvWFP, delimiter=';')
writer.writerow(["Variable Name","Variable File","Variable Line", "Init Fault Time", "End Fault Time", "Fault Mode", "dirName"])
csvWFP.close()

for rootDir in folders:
    print ("Processing folder:", rootDir)
    for dirName, subdirList, fileList in os.walk(rootDir):
        processDirectory(dirName, fileList)

fp = open(csvName+"_"+summFilename, "w")
fp.write("bitflips:;"+str(flipCount))
fp.write("\nSDCs:;"+str(sdcCount))
fp.write("\nCrashes:;"+str(crashCount))
fp.write("\nSimultaneous SDCs and Crashes:;"+str(sdcCrashCount))
fp.write("\n\n")

flipsFM = Counter(faultModeList).most_common()
sdcFM = Counter(faultModeSDCList).most_common()
crashFM = Counter(faultModeCrashList).most_common()
fp.write("\nFault Modes #flips:")
for k,v in sorted(flipsFM):
    fp.write("\n"+k+";"+str(v))
fp.write("\nFault Modes #SDC:")
for k,v in sorted(sdcFM):
    fp.write("\n"+k+";"+str(v))
fp.write("\nFault Modes #Crashes:")
for k,v in sorted(crashFM):
    fp.write("\n"+k+";"+str(v))

flipsTF = Counter(timeFrameList).most_common()
sdcTF = Counter(timeFrameSDCList).most_common()
crashTF = Counter(timeFrameCrashList).most_common()
fp.write("\n\nTime Frame #flips:")
for k,v in sorted(flipsTF):
    fp.write("\n"+k+";"+str(v))
fp.write("\nTime Frame #SDC:")
for k,v in sorted(sdcTF):
    fp.write("\n"+k+";"+str(v))
fp.write("\nTime Frame #Crashes:")
for k,v in sorted(crashTF):
    fp.write("\n"+k+";"+str(v))

flips = Counter(flipList)

fp.write("\n\nVariables that caused SDCs:")
fp.write("\nPVF ;#flips ;#SDCs ;Var name ;file ;line number")
for k,v in Counter(varSDCList).most_common():
    pvf = float(v)/float(flips[k]) * 100
    fp.write("\n"+str(pvf)+";"+str(flips[k])+";"+str(v)+";"+k)

fp.write("\n")
fp.write("\nVariables that caused Crash:")
fp.write("\nPVF ;#flips ;#SDCs ;Var name ;file ;line number")
for k,v in Counter(varCrashList).most_common():
    pvf = float(v)/float(flips[k]) * 100
    fp.write("\n"+str(pvf)+";"+str(flips[k])+";"+str(v)+";"+k)

fp.close()

