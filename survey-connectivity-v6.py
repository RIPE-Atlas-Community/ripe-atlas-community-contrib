#!/usr/bin/env python

import RIPEAtlas

import time
import sys

targets = ("www.afnic.fr", "www.ietf.org", "www.icann.org", "www.wikipedia.org",
           "www.freebsd.org", "www.google.com")
requested = 1000

data = { "definitions": [
    { "type": "ping", "af": 6, "is_oneoff": True, "packets": 3} ],
         "probes": [
             {"requested": requested, "type": "area", "value": "WW"}] }
first = True
probes = {}
for target in targets:
    data["definitions"][0]["target"] = target
    data["definitions"][0]["description"] = "IPv6 base connectivity tests with %s" % target
    if not first:
        # Reuse the same probes
        data["probes"][0]["type"] = "msm"
        data["probes"][0]["value"] = measurement.id
    else:
        first = False
    measurement = RIPEAtlas.Measurement(data,
                                        lambda delay: sys.stderr.write(
                                            "Sleeping %i seconds...\n" % delay))
    print "Measurement #%s to %s uses %i probes" % (measurement.id, target,
                                                    measurement.num_probes)
    results = measurement.results(wait=True)
    num_success = 0
    num_error = 0
    num_tests = 0
    num_probe_timeout = 0
    num_probe_other_errors = 0
    print("%s probes reported" % len(results))
    for result in results:
        probe = result["prb_id"]
        probe_success = False
        probe_timeout = False
        probe_error = False
        if probes.has_key(probe):
            pass
        else:
            probes[probe] = False
        for test in result["result"]:
            num_tests += 1
            if test.has_key("rtt"):
                num_success += 1
                probes[probe] = True
                probe_success = True
                break
            elif test.has_key("error"):
                probe_error = True
            elif test.has_key("x"):
                probe_timeout = True
            else:
                print >>sys.stderr, ("Result for probe %s has no field rtt, or x or error" % \
                                     probe)
                sys.exit(1)
        if not probe_success:
            num_error += 1
            if probe_timeout and not probe_error:
                num_probe_timeout += 1
            elif probe_error and not probe_timeout:
                num_probe_other_errors += 1
            else:
                pass # We count only when all the failures are the same
    print ("Test done at %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    print("%i successful probes (%.1f %%), %i probes without any success (%.1f %%)" % \
              (num_success, num_success*100.0/measurement.num_probes, 
               num_error, num_error*100.0/measurement.num_probes))
    print "\tAmong the total failures, %i timeouts (%.1f %%) and %i explicit errors (%.1f %%)" % \
          (num_probe_timeout, num_probe_timeout*100.0/num_error,
           num_probe_other_errors, num_probe_other_errors*100.0/num_error)
    print ""
complete_fails = 0
for probe in probes:
    if not probes[probe]:
        complete_fails += 1
        print "Failing probe %s" % probe
print "%.1f %% of the probes cannot ping any of the targets" % (complete_fails*100.0/len(probes))

