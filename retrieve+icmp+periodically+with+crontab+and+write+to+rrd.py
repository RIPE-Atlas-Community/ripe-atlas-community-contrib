#!/usr/bin/python

""" Python code to retrieve RIPE Atlas UDMs. 
This one is for retrieving IPv4 ICMP Measurements 
periodically, every 300 seconds, and write the results into a Round Robin Database.

You'll need an API key in '/home/user0/ripeatlas/.atlas/auth_Download' 
the script under /home/user0/ripeatlas/
and the python-rrdtool library. 

The RIPE UDM is configured to send 3 icmps and take place every 300 seconds.
Crontab runs the script that retrieves the JSON results every 300 seconds too.
Results are stored on a RRD - Round Robin Database(rrdtool).
Two PNG Files are created from the RRD every 16 Minutes.

Usage: script.py [measurement_id] [probe_id1/probe_id2/probe_idx] [database.rrd]
* Rename the file to script.py *

Crontab example: 
m       h       dom     mon     dow     command
*/5     *       *       *       *       /usr/bin/python /home/user0/ripeatlas/script.py 1421802 12239/13314 AS3320_latency_db.rrd
*/16    *       *       *       *       /home/user0/ripeatlas/AS3320_roundtriptime_graph.sh >> /dev/null 2>&1
*/16    *       *       *       *       /home/user0/ripeatlas/AS3320_packetloss_graph.sh >> /dev/null 2>&1

Example is complemented using the following bash scripts: 
AS3320_create_RRD.sh
AS3320_roundtriptime_graph.sh
AS3320_packetloss_graph.sh

Based on Stephane Bortzmeyer <bortzmeyer@nic.fr> scripts.

Daniel Gomez <daniel.gomez@synaix.de>

"""

import urllib2
import urllib
import json
import os
import sys
import time
from decimal import *
import re
import string
import rrdtool

       
# Substitutes "/" with "," (Some monitoring tools do not allow the symbol ",")
def sub_string(s):
	return regex.sub(',', s)

# Punctuation string for Probe_id formatting
try:
	regex = re.compile('[%s]' % re.escape(string.punctuation))
except:
	raise Exception("Not posible to create regex")

# Defines the decimal precision for geometric mean calculations.
try:
	getcontext().prec = 8
except:
	raise Exception("Precision not available")

# Url from RIPE
url = "https://atlas.ripe.net/api/v1/measurement/"

# API Key
authfile = "/home/user0/ripeatlas/.atlas/auth_Download"

# Check if the API key file exists.
if not os.path.exists(authfile) or os.stat(authfile)[6]==0:
	raise Exception("API Key File does not exists or it is empty")

# Open the API key file and Retrieve the ID.
auth = open(authfile)
key = auth.readline()[:-1]
auth.close()

# Script Variables
timeouts = 0
total_avg = 0
num_avg = 0
geomean_rtt = 1
geomean = 0
total_rtt = 0
num_rtt = 0
num_error = 0
pl = 100
icmps = 3

# Usage is "Measurement ID" "Probe ID1/ProbeID2/ProbeIDx" "RRDdatabase"
if len(sys.argv) > 4 or len(sys.argv) < 4:
	print >>sys.stderr, ("Usage: %s [measurement_id] [probe_id1/probe_idx] [database.rrd]"
		% sys.argv[0])
	raise Exception("Wrong Input Usage")
elif len(sys.argv) == 4:
	measure = int(sys.argv[1])
	noformids = str(sys.argv[2])
	rrddatabase = str(sys.argv[3])
	probeid = sub_string(noformids)
else:
	raise Exception("Input Parameter Error")

# We look for the Round Robin Database
rrddb = "/home/user0/ripeatlas/" + rrddatabase
if not os.path.exists(rrddb) or os.stat(rrddb)[6]==0:
	raise Exception("RRD Database does not exist")

# Optional: Alternate file to save the measurements
#MeasList = "/home/user0/ripeatlas/.atlas/MeasList" + (str(sys.argv[1]) + "-" + probeid)
#if not os.path.exists(MeasList):
#	CreateMeasList = open(MeasList, "w")
#	CreateMeasList.close()

# Measurements run in Central European Time, apply your own time!
now = int((time.time() - 3600))

# With the following file we track the last time 
# we have asked RIPE for the JSON data.
# If the file does not exist we create a new one.
timetrackerfile = "/home/user0/ripeatlas/.atlas/" + (str(sys.argv[1]) + "-" + probeid)

if os.path.exists(timetrackerfile) and not os.stat(timetrackerfile)[6]==0:
	timetracker = open(timetrackerfile, "r")
	start = int(float(timetracker.readline()[:-1]))
	timetracker.close()
else:
	start = now

timetracker = open(timetrackerfile, "w")
timetracker.write("%f\n" % (now))
timetracker.close()
	
# Check the status of an Ongoing measurement
request = urllib2.Request("%s/%i/?start=%i&stop=%i&prb_id=%s&key=%s" %
	(url, measure, start, now, probeid, key))
request.add_header("Accept", "application/json")
try:
	conn = urllib2.urlopen(request)
	results = json.load(conn)
	conn.close()
	status = results["status"]["name"]
	# The measurement must be running in order to retrieve information.
	if status == "Ongoing" or status == "Specified":
		req = urllib2.Request("%s/%i/result/?start=%i&stop=%i&prb_id=%s&key=%s" %
			(url, measure, start, now, probeid, key))
		req.add_header("Accept", "application/json")
		try:
			connec = urllib2.urlopen(req)
			results = json.load(connec)
			connec.close()
			# We iterate over the JSON data.
			for result in results:
				# We check if the result field exist.
				if ("result" in result):
					# "avg":-1 means,probes have not hitted the destination.
					if ("avg" in result != -1):
						total_avg += Decimal(result["avg"])
						num_avg += 1
					for test in result["result"]:
						if "x" in test:
							timeouts += 1
						elif "rtt" in test:
							total_rtt += Decimal(test["rtt"])
							num_rtt += 1
							geomean_rtt *= Decimal(test["rtt"])
						elif "error" in test:
							num_error += 1
		except:
			# Should not happen since we have already called the web some milliseconds ago.
			ret = rrdtool.update('%s' % rrddb, 'N:%s:%s' % (pl, geomean))
			if ret:
				print rrdtool.error()
				time.sleep(5)
		# If there exist valid results we calculate the geometric mean and packet loss % 
		if num_rtt > 0 and geomean_rtt > 1:
			geomean = (geomean_rtt ** (Decimal(1.0) / num_rtt))
			pl = int(100 - ((num_rtt * 100) / (num_avg * icmps)))
			# Now, we update the rrd databae.
			try:
				ret = rrdtool.update('%s' % rrddb, 'N:%s:%s' % (pl, geomean))
				if ret:
					print rrdtool.error()
					time.sleep(5)
			except:
				print ("Unable to update rrd database")
				raise
		else:
                	# The system is probably not reachable since there are not any valid results.
                	# "avg":-1 and "rcvd":0 are a hint.
			try:
				ret = rrdtool.update('%s' % rrddb, 'N:%s:%s' % (pl, geomean))
				if ret:
					print rrdtool.error()
					time.sleep(5)
			except:
				print ("Unable to update rrd database")
				raise
		# Optional: Results are write to a file.
		#try:
		#	savemeas = open(MeasList, "a")
		#	savemeas.write("%i,%i,%f,%f,%i,%i\n" % (num_avg, num_rtt, geomean, total_rtt / num_rtt, now, start))
		#	savemeas.close()
		#except:
		#	print ("Unable to save measurement")
		#	raise

	else:
		print ("Measurement is probably stopped")
		raise
except:
	# That could mean, that the system that contains the script
	# cannot reach the Url from RIPE, for example during a dsl reconnection,
	# or RIPE is not reachable (not so common).
	ret = rrdtool.update('%s' % rrddb, 'N:%s:%s' % (pl, geomean))
	if ret:
		print rrdtool.error()
		time.sleep(5)
