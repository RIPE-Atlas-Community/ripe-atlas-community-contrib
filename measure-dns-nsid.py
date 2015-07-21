#!/usr/bin/env python

""" Python code to start a RIPE Atlas UDM (User-Defined
Measurement). This one is for running DNS NSID queries (find the
identity of a name server).

By default, it runs measurements in six geographical areas. You can
use -l to run it on specific probes instead.

It outputs the ID of the measurements.

Stephane Bortzmeyer <bortzmeyer@nic.fr>
"""

import urllib2
import urllib
import json
import time
import sys
import time
import getopt
import os
import string

# Default values
family = 4
selection = "area"
query = "fr"
qtype = "SOA"
num_probes = 500
one_area = False

# Parameters
descr =  "Check identity of %s anycast instance"
data = { "definitions": [
    {"packets": 1, "use_NSID": True,
      "query_argument": query, "query_class": "IN", "query_type": qtype,
      "type": "dns", "is_oneoff": True} ],
         "probes": []}
authfile = "%s/.atlas/auth" % os.environ['HOME']

class CredentialsNotFound(Exception):
    pass

class JsonRequest(urllib2.Request):
    def __init__(self, url):
        urllib2.Request.__init__(self, url)
        self.add_header("Content-Type", "application/json")
        self.add_header("Accept", "application/json")
    
def usage(msg=None):
    print >>sys.stderr, "Usage: %s [-4] [-6] [-q name] [-n N] [-l N,N,N...] target" % sys.argv[0]
    if msg is not None:
        print >>sys.stderr, msg

try:
    optlist, args = getopt.getopt (sys.argv[1:], "46q:t:n:l:ho",
                               ["list_probes=", "type=", "number=",
                                "one_area",
                                "query=", "help"])
    for option, value in optlist:
        if option == "--help" or option == "-h":
            usage()
            sys.exit(0)
        elif option == "--list_probes" or option == "-l":
            probes = string.split(value, ',')
            selection = "list"
        elif option == "--query" or option == "-q":
            query = value
        elif option == "--one_area" or option == "-o":
            one_area = True
        elif option == "--type" or option == "-t":
            qtype = value
        elif option == "--number" or option == "-n":
            num_probes = int(value)
        elif option == "-4":
            family = "4"
        elif option == "-6":
            family = "6"
        else:
            # Should never occur, it is trapped by getopt
            print >>sys.stderr, "Unknown option %s" % option
            usage()
            sys.exit(1)
except getopt.error, reason:
    usage(reason)
    sys.exit(1)
if len(args) != 1:
    usage()
    sys.exit(1)
target = args[0]
data["definitions"][0]["af"] = family
data["definitions"][0]["target"] = target
data["definitions"][0]["query"] = query
data["definitions"][0]["query_type"] = qtype
data["definitions"][0]["description"] = descr % target
if selection == "area":
    data["probes"].append({ "requested": num_probes, "type": "area" })
elif selection == "list":
    data["probes"].append({ "requested": len(probes), "type": "probes", "value": string.join(probes,',') })
else:
    print >>sys.stderr, "Internal error, invalide selection \"%s\"" % selection
    sys.exit(1)
if not os.path.exists(authfile):
    raise CredentialsNotFound(authfile)
auth = open(authfile)
key = auth.readline()[:-1]
auth.close()
url = "https://atlas.ripe.net/api/v1/measurement/?key=%s" % key

if selection == "area":
    if one_area:
        list_areas = ["WW", ]
    else:
        list_areas = ["WW", "West", "North-East", "South-East", "North-Central", "South-Central"]
    for area in list_areas:
        data["probes"][0]["value"] = area
        json_data = json.dumps(data)
        try:
            request = JsonRequest(url)
            conn = urllib2.urlopen(request, json_data)
            results = json.load(conn) # TODO: error handling
            print "%s: measurement #%s" % (area, results["measurements"])
            conn.close()
        except urllib2.HTTPError as e:
            print >>sys.stderr, ("Fatal error: %s" % e.read())
            raise
        conn.close()
elif selection == "list":
    json_data = json.dumps(data)
    try:
        request = JsonRequest(url)
        conn = urllib2.urlopen(request, json_data)
        results = json.load(conn) 
        print "%s: measurement #%s" % (probes, results["measurements"])
        conn.close()
    except urllib2.HTTPError as e:
        print >>sys.stderr, ("Fatal error: %s" % e.read())
        raise
    conn.close()
