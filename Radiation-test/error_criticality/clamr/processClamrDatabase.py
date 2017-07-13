#!/usr/bin/env python

import sys
import os
import csv
import re
import collections
import parseUtils
import shelve


def processErrors(benchmarkname_machinename, sdcItemList):
	benchmark = "CLAMR"
	machine = benchmarkname_machinename
	m = re.match("(.*)_(.*)", benchmarkname_machinename)
	if m:
		benchmark = m.group(1)
		machine = m.group(2)

        benchmark = benchmark.strip()
        machine = machine.strip()

	sdci = 1
	total_sdcs = len(sdcItemList)
        errLimitList = [0.1,0.2,0.3,0.4,0.5,1,2,3,4,5,8,10,12,15]
        csvHeader = list()
        csvHeader.append("logFileName")
        csvHeader.append("machine")
        csvHeader.append("benchmark")
        csvHeader.append("header")
        csvHeader.append("sdcIteration")
        csvHeader.append("numberIterationErrors")
        csvHeader.append("numberIterationErrorsLogged")
        csvHeader.append("numberIterationErrorsParsed")
        csvHeader.append("maxRelativeError")
        csvHeader.append("minRelativeError")
        csvHeader.append("averageRelativeError")
        for errLimit in errLimitList:
            csvHeader.append("numberErrorsLessThan"+str(errLimit))
            csvHeader.append("localityForErrorsHigherThan"+str(errLimit))
        csvHeader.append("numberZeroOutput")
        csvHeader.append("numberZeroGold")

	for sdcItem in sdcItemList:
		progress = "{0:.2f}".format(float(sdci)/float(total_sdcs) * 100)
		sys.stdout.write("\r"+benchmark+" - Processing SDC "+str(sdci)+" of "+str(total_sdcs)+" - "+progress+"%")
		sys.stdout.flush()

		logFileName = sdcItem[0]
		header = sdcItem[1]
                header = header.strip()
		header = re.sub(r"[^\w]", '-', header) #keep only numbers and digits
                header = header.strip()
		sdcIteration = sdcItem[2]
		iteErrors = sdcItem[3]
		errList = sdcItem[4]

                csvOutDict = dict()
                csvOutDict["logFileName"] = logFileName
                csvOutDict["machine"] = machine
                csvOutDict["benchmark"] = benchmark
                csvOutDict["header"] = header
                csvOutDict["sdcIteration"] = sdcIteration
                csvOutDict["numberIterationErrors"] = iteErrors

		
		logFileNameNoExt = logFileName
		m = re.match("(.*).log", logFileName)
		if m:
			logFileNameNoExt = m.group(1)


                csvOutDict["numberIterationErrorsLogged"] = len(errList)
                errorsParsed = errList
                if errorsParsed is None:
                    sdci += 1
                    continue
                csvOutDict["numberIterationErrorsParsed"] = len(errorsParsed)
                (csvOutDict["numberZeroOutput"], csvOutDict["numberZeroGold"] ) = parseUtils.countZerosReadExpected(errorsParsed)

                for errLimit in errLimitList:
                    (maxRelErr, minRelErr, avgRelErr, relErrLowerLimit, errListFiltered) = parseUtils.relativeErrorParser(errorsParsed, errLimit)
                    csvOutDict["maxRelativeError"] = maxRelErr
                    csvOutDict["minRelativeError"] = minRelErr
                    csvOutDict["averageRelativeError"] = avgRelErr
                    csvOutDict["numberErrorsLessThan"+str(errLimit)] = relErrLowerLimit
                    csvOutDict["localityForErrorsHigherThan"+str(errLimit)] = parseUtils.localityMultiDimensional(errListFiltered)



		# Write info to csv file
                csvFileName = "logs_parsed_machine-"+machine+"_benchmark-"+benchmark+"_header-"+header+".csv"
                csvFullPath = os.path.join(csvDirOut, csvFileName)
		if not os.path.exists(os.path.dirname(csvFullPath)):
			try:
				os.makedirs(os.path.dirname(csvFullPath))
			except OSError as exc: # Guard against race condition
				if exc.errno != errno.EEXIST:
				    raise
                if not os.path.isfile(csvFullPath):
		    csvWFP = open(csvFullPath, "a")
		    writer = csv.writer(csvWFP, delimiter=';')
                    writer.writerow(csvHeader)
                else:
		    csvWFP = open(csvFullPath, "a")
		    writer = csv.writer(csvWFP, delimiter=';')
                row = list()
                for item in csvHeader:
                    if item in csvOutDict:
                        row.append(csvOutDict[item])
                    else:
                        row.append(" ")
                writer.writerow(row)

		csvWFP.close()
		sdci += 1

	sys.stdout.write("\r"+benchmark+" - Processing SDC "+str(sdci-1)+" of "+str(total_sdcs)+" - 100%                     "+"\n")
	sys.stdout.flush()
################ => processErrors()


###########################################
# MAIN
###########################################
csvDirOut = "csv_logs_parsed"
print "\n\tCSV files will be stored in "+csvDirOut+"\n"

#db = shelve.open("errors_log_database") #python2
db = shelve.open("clamr_errors_log_database1") #python2
#for k, v in db.items(): #python3
for k, v in db.iteritems(): #python2
	processErrors(k,v)
db.close()

db = shelve.open("clamr_errors_log_database2") #python2
#for k, v in db.items(): #python3
for k, v in db.iteritems(): #python2
	processErrors(k,v)
db.close()

db = shelve.open("clamr_errors_log_database3") #python2
#for k, v in db.items(): #python3
for k, v in db.iteritems(): #python2
	processErrors(k,v)
db.close()
