#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Measurement of the actual connectivity of dot-zero
addresses. Dot-zero addresses are IPv4 addresses with the last byte
being zero. If the prefix length is != 24, these addresses are legal,
but they are rejected by some broken IP stacks.

The addresses are to be found in an external file, one network
per-line, addresses are whitespace separated. For instance:
192.168.1.0 192.168.1.42

Stephane Bortzmeyer <bortzmeyer@nic.fr>
From an idea by Xavier Beaudouin <kiwi@oav.net>
With help from Jean-Philippe Pick <pick@nic.fr>
"""

requested = 1000
verbose = True

import RIPEAtlas

# https://github.com/drkjam/netaddr/
import netaddr

import time
import sys
import re
import collections

class Network:
    def __init__(self, first, normal, last=None):
        """ Initializes with three addresses, expressed as strings:
        one dot-zero, one"normal" and an (optional) one ending in
        .255.  All *must* reply to ping."""
        if not re.search("\.0$", first):
            raise Exception("Invalid first value %s" % first)
        self.first = netaddr.IPAddress(first)
        self.first_msm = None
        self.normal = netaddr.IPAddress(normal)
        self.normal_msm = None
        if last is not None:
            if not re.search("\.255$", last):
                raise Exception("Invalid last value %s" % last)
            self.last = netaddr.IPAddress(last)
            self.last_msm = None
        else:
            self.last = None
    def __str__(self):
        return "%s %s %s" % (self.first, self.normal, self.last)

class Stats:
    def __init__(self):
        self.success = 0
        self.error = 0
        self.probe = 0
        
data = { "definitions": [
    { "type": "ping", "af": 4, "is_oneoff": True, "packets": 3} ],
         "probes": [
             {"requested": requested, "type": "area", "value": "WW"}] }

if len(sys.argv) != 2:
    raise Exception("Usage: %s filename" % sys.argv[0])
thefile = open(sys.argv[1])
networks = []
for line in thefile.readlines():
    line = re.sub("\s*#.*$", "", line)
    # Trim
    line = re.sub("^\s*", "", line)
    line = re.sub("\s*$", "", line)
    if line != "":
        addrs = re.split("\s*", line)
        if len(addrs) == 3:
            networks.append(Network(addrs[0], addrs[1], addrs[2]))
        elif len(addrs) == 2:
            networks.append(Network(addrs[0], addrs[1]))
        else:
            print >>sys.stderr, ("Invalid line \"%s\"", line)
            sys.exit(1)
thefile.close()

for network in networks:
    first = True
    for typpe in ["first", "normal", "last"]:
        if typpe == "last" and network.last is None:
            continue
        if typpe == "first":
            target = network.first
        elif typpe == "normal":
            target = network.normal
        elif typpe == "last":
            target = network.last
        else:
            raise Exception("Internal error")
        data["definitions"][0]["target"] = str(target)
        data["definitions"][0]["description"] = "IPv4 base connectivity tests with %s" % target
        if not first:
            # Reuse the same probes
            data["probes"][0]["type"] = "msm"
            data["probes"][0]["value"] = measurement.id
        else:
            first = False
        measurement = RIPEAtlas.Measurement(data)
        if verbose:
            print "Measurement #%s to %s uses %i probes" % (measurement.id, target,
                                                        measurement.num_probes)
        if typpe == "first":
            network.first_msm = measurement
        elif typpe == "normal":
            network.normal_msm = measurement
        elif typpe == "last":
            network.last_msm = measurement 

total = collections.defaultdict(Stats)
for network in networks:
    if verbose:
        print "Network %s" % network
    for typpe in ["first", "normal", "last"]:
        if typpe == "last" and network.last is None:
            continue
        if typpe == "first":
            results = network.first_msm.results(wait=True, percentage_required=0.99)
            theid = network.first_msm.id
            target = network.first
        elif typpe == "normal":
            results = network.normal_msm.results(wait=True, percentage_required=0.99)
            theid = network.normal_msm.id
            target = network.normal
        elif typpe == "last":
            results = network.last_msm.results(wait=True, percentage_required=0.99)
            theid = network.last_msm.id
            target = network.last
        num_success = 0
        num_error = 0
        num_probe = 0
        if verbose:
            print("%s probes reported for measurement %i" % (len(results), theid))
        for result in results:
            probe = result["prb_id"]
            if re.search("\.0$", result["from"]) or re.search("\.255$", result["from"]):
                if verbose:
                    print >>sys.stderr, ("Ignoring probe %s which has a potentially problematic address %s" % \
                                         (probe, result["from"]))
                continue
            probe_success = False
            num_probe += 1
            for test in result["result"]:
                if test.has_key("rtt"):
                    probe_success = True
                    break
                elif test.has_key("error"):
                    pass
                elif test.has_key("x"):
                    pass
                else:
                    print >>sys.stderr, ("Result for probe %s has no field rtt, or x or error" % \
                                         probe)
                    sys.exit(1)
            if not probe_success:
                num_error += 1
                total[typpe].error += 1
            else:
                num_success += 1
        if num_success > 0: # Otherwise, it means the target is probably dead
            total[typpe].probe += num_probe
            total[typpe].success += num_success
            total[typpe].error += num_error
        else:
            print >>sys.stderr, ("Ignoring target %s which seems down" % target)
        if verbose:
            print "\"%s\" %s successes/%s (%.1f %%)" % \
                  (typpe, num_success, num_probe,
                   num_success*100.0/(num_probe))
    if verbose:
        print ""

print "%i networks" % (len(networks))
print "For the first (dot-zero) address: %s successes/%s (%.1f %%)" % \
      (total["first"].success, total["first"].probe,
       total["first"].success*100.0/total["first"].probe)
print "For the \"normal\" address: %s successes/%s (%.1f %%)" % \
      (total["normal"].success, total["normal"].probe,
       total["normal"].success*100.0/total["normal"].probe)
print "For the last (.255 address: %s successes/%s (%.1f %%)" % \
      (total["last"].success, total["last"].probe,
       total["last"].success*100.0/total["last"].probe)
