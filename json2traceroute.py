#!/usr/bin/python

import sys
import json
from cymruwhois import Client
import cPickle as pickle
import time

if len(sys.argv) != 2:
    print >> sys.stderr, "Usage: json2traceroute.py file"
    sys.exit(1)

json_file = sys.argv[1]
data = json.load(file(json_file))

def whoisrecord(ip):
    currenttime = time.time()
    ts = currenttime
    if ip in whois:
        ASN,ts = whois[ip]
    else:
        ts = 0
    if ((currenttime - ts) > 36000):
        C = Client()
        ASN = C.lookup(ip)
        whois[ip] = (ASN,currenttime)
    return ASN

try:
    pkl_file = open('whois.pkl', 'rb')
    whois = pickle.load(pkl_file)
except IOError:
    whois = {}

# Create traceroute output
try:
    for probe in data:
        probefrom = probe["from"]
        if probefrom:
            ASN = whoisrecord(probefrom)
        print "From: ",probefrom,"  ",ASN.asn,"  ",ASN.owner
        print "Source address: ",probe["src_addr"]
        print "Probe ID: ",probe["prb_id"]
        result = probe["result"]
        for proberesult in result:
            ASN = {}
            if "result" in proberesult:
                print proberesult["hop"],"  ",
                hopresult = proberesult["result"]
                rtt = []
                hopfrom = ""
                for hr in hopresult:
                    if "error" in hr:
                        rtt.append(hr["error"])
                    elif "x" in hr:
                        rtt.append(hr["x"])
                    elif "edst" in hr:
                        rtt.append("!")
                    else:
                        rtt.append(hr["rtt"])
                        hopfrom = hr["from"]
                        ASN = whoisrecord(hopfrom)
                if hopfrom:
                    print hopfrom,"  ",ASN.asn,"  ",ASN.owner,"  ",
                print rtt
            else:
                print "Error: ",proberesult["error"]
        print ""

finally:
    pkl_file = open('whois.pkl', 'wb')
    pickle.dump(whois, pkl_file)


