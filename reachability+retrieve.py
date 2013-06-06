#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is for running IPv4 or IPv6 ICMP queries to
test reachability.

You'll need an API key in ~/.atlas/auth.

After launching the measurement, it downloads the results and analyzes
them.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import urllib2
import urllib
import json
import time
import os
import string
import sys
import time
import socket
import getopt

# Default values
country = None # World-wide
verbose = False
requested = 5 # Probes
tests = 3 # ICMP packets per probe
percentage_required = 0.9 # Percentage of responding probes before we stop

# The following parameters are currently not settable from the
# command-line. Anyway, be careful when changing these, you may get
# inconsistent results if you do not wait long enough. Other warning:
# the time to wait depend on the number of the probes.
# All in seconds:
fields_delay_base = 5
fields_delay_factor = 0.2
results_delay_base = 3
results_delay_factor = 0.15
maximum_time_for_results_base = 30
maximum_time_for_results_factor = 5
# The basic problem is that there is no easy way in Atlas to know when
# it is over, either for retrieving the list of the probes, or for
# retrieving the results themselves. The only solution is to wait
# "long enough". The time to wait is not documented so the values
# above have been found mostly with trial-and-error.

def is_ip_address(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

class JsonRequest(urllib2.Request):
    def __init__(self, url):
        urllib2.Request.__init__(self, url)
        self.add_header("Content-Type", "application/json")
        self.add_header("Accept", "application/json")

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s target-IP-address" % sys.argv[0]
    print >>sys.stderr, """Options are:
    --verbose or -v : makes the program more talkative
    --help or -h : this message
    --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --requested=N or -r N : requests N probes (default is %s)
    --tests=N or -t N : send N ICMP packets from each probe (default is %s)
    --percentage=X or -p X : stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    """ % (requested, tests, percentage_required)

try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:t:p:vh",
                               ["requested=", "country=", "percentage=",
                                "tests=", "verbose", "help"])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--tests" or option == "-t":
            tests = int(value)
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        else:
            # Should never occur, it is trapped by getopt
            usage("Unknown option %s" % option)
            sys.exit(1)
except getopt.error, reason:
    usage(reason)
    sys.exit(1)

if len(args) != 1:
    usage()
    sys.exit(1)
target = args[0]
if not is_ip_address(target):
    print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
    sys.exit(1)

authfile = "%s/.atlas/auth" % os.environ['HOME']
data = { "definitions": [
           { "target": target, "description": "Ping %s" % target,
           "type": "ping", "is_oneoff": True, "packets": tests} ],
         "probes": [
             { "requested": requested} ] }
if country is not None:
    data["probes"][0]["type"] = "country"
    data["probes"][0]["value"] = country
    data["definitions"][0]["description"] += (" from %s" % country)
else:
    data["probes"][0]["type"] = "area"
    data["probes"][0]["value"] = "WW"
    
if not os.path.exists(authfile):
    print >>sys.stderr, ("Authentication file %s not found" % authfile)
    sys.exit(1)
auth = open(authfile)
key = auth.readline()[:-1]
auth.close()

url = "https://atlas.ripe.net/api/v1/measurement/?key=%s" % key
url_probes = "https://atlas.ripe.net/api/v1/measurement/%s/?fields="
url_results = "https://atlas.ripe.net/api/v1/measurement/%s/result/"

request = JsonRequest(url)
if string.find(target, ':') > -1:
    af = 6
else:
    af = 4
data["definitions"][0]['af'] = af
json_data = json.dumps(data)
if verbose:
    print json_data
try:
    # Start the measurement
    conn = urllib2.urlopen(request, json_data)
    # Now, parse the answer
    results = json.load(conn)
    measurement = results["measurements"][0]
    if country is not None:
        where = "@%s" % country
    else:
        where = "world-wide"
    print("%s %s: measurement #%s" % (target, where, measurement))
    conn.close()
except urllib2.HTTPError as e:
    print >>sys.stderr, ("Fatal error when submitting request: %s" % e.read())
    sys.exit(1)

# Find out how many probes were actually allocated to this measurement
enough = False
fields_delay = fields_delay_base + (requested * fields_delay_factor)
while not enough:
    # Let's be patient
    if (verbose and fields_delay > 30):
        print "%s sleeping %i seconds..." % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                          fields_delay)
    time.sleep(fields_delay)
    fields_delay *= 2
    request = JsonRequest(url_probes % measurement)
    try:
        conn = urllib2.urlopen(request)
        # Now, parse the answer
        meta = json.load(conn)
        if meta["status"]["name"] == "Specified" or meta["status"]["name"] == "Scheduled":
            # Not done, loop
            if verbose:
                print "%s list of allocated probes not ready" % \
                      time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) 
        elif meta["status"]["name"] == "Ongoing":
            enough = True
            num_probes = len(meta["probes"])
            print "%s probes allocated" % num_probes
        else:
            print >>sys.stderr, meta
            print >>sys.stderr, ("Internal error, unexpected status when querying the measurement fields: \"%s\"" % meta["status"])
            sys.exit(1) 
        conn.close()
    except urllib2.HTTPError as e:
        print >>sys.stderr, ("Fatal error when querying fields: %s" % e.read())
        sys.exit(1) 

# Retrieve the results
enough = False
attempts = 0
results_delay = results_delay_base + (num_probes * results_delay_factor)
maximum_time_for_results = maximum_time_for_results_base + \
    (num_probes * maximum_time_for_results_factor)
start = time.time()
elapsed = 0
while not enough and elapsed < maximum_time_for_results:
    if (verbose and results_delay > 30):
        print "Sleeping %i seconds..." % results_delay
    time.sleep(results_delay) 
    results_delay *= 2
    request = JsonRequest(url_results % measurement)
    attempts += 1
    elapsed = time.time() - start
    try:
        conn = urllib2.urlopen(request)
        data = json.load(conn) 
        num_results = len(data)
        if num_results >= num_probes*percentage_required: # Requesting a strict
                                         # equality may be too strict:
                                         # if an allocated probe does
                                      # not respond, we will have to
                                      # wait for the stop of the
                                      # measurement (many
                                      # minutes). Anyway, there is
                                      # also the problem that a probe
                                      # may have sent only a part of
                                      # its measurements.
            enough = True
        else:
            status = meta["status"]["name"]
            if status == "Ongoing":
                # Wait a bit more
                if verbose:
                    print "%s measurement not over, only %s/%s probes reported" % \
                          (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                           num_results, num_probes)
            elif status == "Stopped":
                enough = True # Even if not enough probes
            else:
                print >>sys.stderr, \
                      ("Internal error, unexpected status when retrieving the measurement: \"%s\"" % \
                       meta["status"])
                sys.exit(1)
        conn.close()
    except urllib2.HTTPError as e:
        print >>sys.stderr, ("Fatal error when reading results: %s" % e.read())
        sys.exit(1)
if verbose and elapsed > maximum_time_for_results:
    print "Maximum wait time (%i s) elapsed, working with the results we have..." % maximum_time_for_results

total_rtt = 0
num_rtt = 0
num_error = 0
num_timeout = 0
num_tests = 0
print("%s probes reported" % len(data))
for result in data:
    for test in result["result"]:
        num_tests += 1
        if test.has_key("rtt"):
            total_rtt += int(test["rtt"])
            num_rtt += 1
        elif test.has_key("error"):
            num_error += 1
        elif test.has_key("x"):
            num_timeout += 1
        else:
            print >>sys.stderr, ("Result has no field rtt, or x or error")
            sys.exit(1)
print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
if num_rtt == 0:
    print("No successful test")
else:
    print("Tests: %i successful tests (%.1f %%), %i errors (%.1f %%), %i timeouts (%.1f %%), average RTT: %i ms" % \
          (num_rtt, num_rtt*100.0/num_tests, 
           num_error, num_error*100.0/num_tests, 
           num_timeout, num_timeout*100.0/num_tests, total_rtt/num_rtt))
