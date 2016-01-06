#!/usr/bin/python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is for running IPv4 or IPv6 ICMP queries to
test reachability.

You'll need an API key in ~/.atlas/auth.

After launching the measurement, it downloads the results and analyzes
them.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import json
import time
import os
import string
import sys
import time
import getopt
import socket
import collections

import RIPEAtlas

# Default values
country = None # World-wide
asn = None # All
area = None # World-wide
old_measurement = None
measurement_id = None
prefix = None # All
verbose = False
requested = 5 # Probes
tests = 3 # ICMP packets per probe
by_probe = False # Default is to count by test, not by probe
percentage_required = 0.9
the_probes = None
exclude = None
include = None
display_probes = False
machine_readable = False

class Set():
    def __init__(self):
        self.failed = True
        
def is_ip_address(str):
    try:
        addr = socket.inet_pton(socket.AF_INET6, str)
    except socket.error: # not a valid IPv6 address
        try:
            addr = socket.inet_pton(socket.AF_INET, str)
        except socket.error: # not a valid IPv4 address either
            return False
    return True

def usage(msg=None):
    if msg:
        print >>sys.stderr, msg
    print >>sys.stderr, "Usage: %s target-IP-address ..." % sys.argv[0]
    print >>sys.stderr, """Options are:
    --verbose or -v : makes the program more talkative
    --machinereadable or -b : machine-readable output, to be consumed by tools like grep or cut
    --help or -h : this message
    --displayprobes or -o : display the failing probes numbers (WARNING: may create a big list)
     --country=2LETTERSCODE or -c 2LETTERSCODE : limits the measurements to one country (default is world-wide)
    --area=AREACODE or -a AREACODE : limits the measurements to one area such as North-Central (default is world-wide)
    --asn=ASnumber or -n ASnumber : limits the measurements to one AS (default is all ASes)
    --probes=N or -s N : selects the probes by giving explicit ID (one ID or a comma-separated list)
    --prefix=PREFIX or -f PREFIX : limits the measurements to one IP prefix (default is all prefixes)
    --old_measurement MSMID or -g MSMID : uses the probes of measurement #MSMID
    --measurement_ID=N or -m N : do not start a measurement, just analyze a former one 
    --include TAGS or -i TAGS : limits the measurements to probes with these tags (a comma-separated list)
    --exclude TAGS or -e TAGS : excludes from measurements the probes with these tags (a comma-separated list)
    --requested=N or -r N : requests N probes (default is %s)
    --tests=N or -t N : send N ICMP packets from each probe (default is %s)
    --by_probe : count the percentage of success by probe, not by test (useless if --tests=1)
    --percentage=X or -p X : stops the program as soon as X %% of the probes reported a result (default is %2.2f)
    """ % (requested, tests, percentage_required)
    
try:
    optlist, args = getopt.getopt (sys.argv[1:], "r:c:a:n:t:p:m:vbhf:g:e:i:os:",
                               ["requested=", "country=", "area=", "prefix=", "asn=", "percentage=", "probes=",
                                "exclude=", "include=", "by_probe",
                                "tests=", "verbose", "machinereadable", "old_measurement=", "measurement_ID=",
                                "displayprobes", "help"])
    for option, value in optlist:
        if option == "--country" or option == "-c":
            country = value
        elif option == "--area" or option == "-a":
            area = value
        elif option == "--asn" or option == "-n":
            asn = value
        elif option == "--prefix" or option == "-f":
            prefix = value
        elif option == "--percentage" or option == "-p":
            percentage_required = float(value)
        elif option == "--probes" or option == "-s":
            the_probes = value # Splitting (and syntax checking...) delegated to Atlas
        elif option == "--requested" or option == "-r":
            requested = int(value)
        elif option == "--tests" or option == "-t":
            tests = int(value)
        elif option == "--exclude" or option == "-e":
            exclude = string.split(value, ",")
        elif option == "--include" or option == "-i":
            include = string.split(value, ",")
        elif option == "--old_measurement" or option == "-g":
            old_measurement = value
        elif option == "--measurement_ID" or option == "-m":
            measurement_id = value
        elif option == "--verbose" or option == "-v":
            verbose = True
        elif option == "--by_probe":
            by_probe = True
        elif option == "--machinereadable" or option == "-b":
            machine_readable = True
        elif option == "--displayprobes" or option == "-o":
            display_probes = True
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

targets = args

if the_probes is not None:
    requested = len(string.split(the_probes,","))
if verbose and machine_readable:
    usage("Specify verbose *or* machine-readable output")
    sys.exit(1)
if display_probes and machine_readable:
    usage("Display probes *or* machine-readable output")
    sys.exit(1)
data = { "definitions": [
           { "type": "ping", "is_oneoff": True, "packets": tests} ],
         "probes": [
             { "requested": requested} ] }
if include is not None or exclude is not None:
    data["probes"][0]["tags"] = {}
if include is not None:
    data["probes"][0]["tags"]["include"] = include
if exclude is not None:
    data["probes"][0]["tags"]["exclude"] = exclude
if the_probes is not None:
    if country is not None or area is not None or asn is not None:
        usage("Specify the probes ID *or* country *or* area *or* ASn")
        sys.exit(1)
    data["probes"][0]["type"] = "probes"
    data["probes"][0]["value"] = the_probes
else:
    if country is not None:
        if asn is not None or area is not None or prefix is not None:
            usage("Specify country *or* area *or* ASn *or* prefix")
            sys.exit(1)
        data["probes"][0]["type"] = "country"
        data["probes"][0]["value"] = country
    elif area is not None:
            if asn is not None or country is not None:
                usage("Specify country *or* area *or* ASn *or* prefix")
                sys.exit(1)
            data["probes"][0]["type"] = "area"
            data["probes"][0]["value"] = area
    elif asn is not None:
            if area is not None or country is not None:
                usage("Specify country *or* area *or* ASn *or* prefix")
                sys.exit(1)
            data["probes"][0]["type"] = "asn"
            data["probes"][0]["value"] = asn
    elif prefix is not None:
            if area is not None or country is not None or asn is not None:
                usage("Specify country *or* area *or* ASn *or* prefix")
                sys.exit(1)
            data["probes"][0]["type"] = "prefix"
            data["probes"][0]["value"] = prefix
    elif old_measurement is not None:
            if area is not None or country is not None or asn is not None:
                usage("Specify country *or* area *or* ASn *or* old measurement")
                sys.exit(1)
    else:
        data["probes"][0]["type"] = "area"
        data["probes"][0]["value"] = "WW"

for target in targets:
    if not is_ip_address(target):
        print >>sys.stderr, ("Target must be an IP address, NOT AN HOST NAME")
        sys.exit(1)
    data["definitions"][0]["target"] = target
    data["definitions"][0]["description"] = "Ping %s" % target
    if country is not None:
        data["definitions"][0]["description"] += (" from %s" % country)
    if area is not None:
        data["definitions"][0]["description"] += (" from %s" % area)
    if asn is not None:
        data["definitions"][0]["description"] += (" from AS #%s" % asn)
    if prefix is not None:
        data["definitions"][0]["description"] += (" from prefix %s" % prefix)
    if string.find(target, ':') > -1:
        af = 6
    else:
        af = 4
    data["definitions"][0]['af'] = af
    if old_measurement is not None:
            data["probes"][0]["requested"] = 500 # Dummy value, anyway,
                                                    # but necessary to get
                                                    # all the probes
            # TODO: the huge value of "requested" makes us wait a very long time
            data["probes"][0]["type"] = "msm"
            data["probes"][0]["value"] = old_measurement
            data["definitions"][0]["description"] += (" from probes of measurement #%s" % old_measurement)
    if measurement_id is None:
        if verbose:
            print data
        measurement = RIPEAtlas.Measurement(data)
        if old_measurement is None:
            old_measurement = measurement.id
        if verbose:
            print "Measurement #%s to %s uses %i probes" % (measurement.id, target,
                                                        measurement.num_probes)
        # Retrieve the results
        rdata = measurement.results(wait=True, percentage_required=percentage_required)
    else:
        measurement = RIPEAtlas.Measurement(data=None, id=measurement_id)
        rdata = measurement.results(wait=False)
        if verbose:
            print "%i results from already-done measurement #%s" % (len(rdata), measurement.id)

    total_rtt = 0
    num_rtt = 0
    num_error = 0
    num_timeout = 0
    num_tests = 0
    if by_probe:
        probes_success = 0
        probes_failure = 0
        num_probes = 0
    if not machine_readable and measurement_id is None:
        print("%s probes reported" % len(rdata))
    if display_probes:
        failed_probes = collections.defaultdict(Set)
    for result in rdata:
        probe_ok = False
        probe = result["prb_id"]
        if by_probe:
            num_probes += 1
        for test in result["result"]:
            num_tests += 1
            if test.has_key("rtt"):
                total_rtt += int(test["rtt"])
                num_rtt += 1
                probe_ok = True
            elif test.has_key("error"):
                num_error += 1
            elif test.has_key("x"):
                num_timeout += 1
            else:
                print >>sys.stderr, ("Result has no field rtt, or x or error")
                sys.exit(1)
        if by_probe:
            if probe_ok:
                probes_success += 1
            else:
                probes_failure += 1
        if display_probes and not probe_ok:
            failed_probes[probe].failed = True
    if not machine_readable:
        print ("Test #%s done at %s" % (measurement.id, time.strftime("%Y-%m-%dT%H:%M:%SZ", measurement.time)))
    if num_rtt == 0:
        if not machine_readable:
            print("No successful test")
    else:
        if not machine_readable:
            if not by_probe:
                print("Tests: %i successful tests (%.1f %%), %i errors (%.1f %%), %i timeouts (%.1f %%), average RTT: %i ms" % \
                    (num_rtt, num_rtt*100.0/num_tests, 
                    num_error, num_error*100.0/num_tests, 
                    num_timeout, num_timeout*100.0/num_tests, total_rtt/num_rtt))
            else:
                print("Tests: %i successful probes (%.1f %%), %i failed (%.1f %%), average RTT: %i ms" % \
                    (probes_success, probes_success*100.0/num_probes, 
                    probes_failure, probes_failure*100.0/num_probes, 
                    total_rtt/num_rtt))
    if len(targets) > 1 and not machine_readable:
        print ""
    if display_probes:
        print failed_probes.keys()
    if machine_readable:
        if num_rtt != 0:
            percent_rtt = total_rtt/num_rtt
        else:
            percent_rtt = 0
        print ",".join([target, str(measurement.id), "%s/%s" % (len(rdata),measurement.num_probes), \
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "%i" % num_rtt, \
                        "%.1f" % (num_rtt*100.0/num_tests), "%i" % num_error, "%.1f" % (num_error*100.0/num_tests), \
                        "%i" % num_timeout, "%.1f" % (num_timeout*100.0/num_tests), "%i" % (percent_rtt)])
