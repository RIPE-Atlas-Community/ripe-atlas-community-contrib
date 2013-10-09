#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" A module to perform measurements on the RIPE Atlas
<http://atlas.ripe.net/> probes using the UDM (User Defined
Measurements) creation API.

Authorization key is expected in $HOME/.atlas/auth or have to be
provided in the constructor's arguments.

Stéphane Bortzmeyer <bortzmeyer+ripe@nic.fr>

"""

import os
import json
import time
import urllib2

authfile = "%s/.atlas/auth" % os.environ['HOME']
base_url = "https://atlas.ripe.net/api/v1/measurement"

# The following parameters are currently not settable. Anyway, be
# careful when changing these, you may get inconsistent results if you
# do not wait long enough. Other warning: the time to wait depend on
# the number of the probes.
# All in seconds:
fields_delay_base = 6
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

class AuthFileNotFound(Exception):
    pass

class RequestSubmissionError(Exception):
    pass

class FieldsQueryError(Exception):
    pass

class ResultError(Exception):
    pass

class InternalError(Exception):
    pass

class JsonRequest(urllib2.Request):
    def __init__(self, url):
        urllib2.Request.__init__(self, url)
        self.add_header("Content-Type", "application/json")
        self.add_header("Accept", "application/json")

class Measurement():
    """ An Atlas measurement, identified by its ID (such as #1010569) in the field "id" """

    def __init__(self, data, wait=True, sleep_notification=None, key=None):
        """ Creates a measurement."data" must be a dictionary (*not* a JSON string) having the members
        requested by the Atlas documentation. "wait" should be set to False for periodic (not
        oneoff) measurements. "sleep_notification" is a lambda taking one parameter, the
        sleep delay: when the module has to sleep, it calls this lambda, allowing you to be informed of
        the delay. "key" is the API key. If None, it will be read in the configuration file."""        
        if not key:
            if not os.path.exists(authfile):
                raise AuthFileNotFound("Authentication file %s not found" % authfile)
            auth = open(authfile)
            key = auth.readline()[:-1]
            auth.close()

        self.url = base_url + "/?key=%s" % key
        self.url_probes = base_url + "/%s/?fields=probes,status"
        self.url_status = base_url + "/%s/?fields=status" 
        self.url_results = base_url + "/%s/result/" 

        self.json_data = json.dumps(data)
        self.notification = sleep_notification
        request = JsonRequest(self.url)
        try:
            # Start the measurement
            conn = urllib2.urlopen(request, self.json_data)
            # Now, parse the answer
            results = json.load(conn)
            self.id = results["measurements"][0]
            conn.close()
        except urllib2.HTTPError as e:
            raise RequestSubmissionError("Status %s, reason \"%s\"" % \
                                         (e.code, e.read()))

        if not wait:
            return
        # Find out how many probes were actually allocated to this measurement
        enough = False
        requested = data["probes"][0]["requested"] 
        fields_delay = fields_delay_base + (requested * fields_delay_factor)
        while not enough:
            # Let's be patient
            if self.notification is not None:
                self.notification(fields_delay)
            time.sleep(fields_delay)
            fields_delay *= 2
            request = JsonRequest(self.url_probes % self.id)
            try:
                conn = urllib2.urlopen(request)
                # Now, parse the answer
                meta = json.load(conn)
                if meta["status"]["name"] == "Specified" or \
                       meta["status"]["name"] == "Scheduled":
                    # Not done, loop
                    pass
                elif meta["status"]["name"] == "Ongoing":
                    enough = True
                    self.num_probes = len(meta["probes"])
                else:
                    raise InternalError("Internal error, unexpected status when querying the measurement fields: \"%s\"" % meta["status"])
                conn.close()
            except urllib2.HTTPError as e:
                raise FieldsQueryError("%s" % e.read())
          
    def results(self, wait=True, percentage_required=0.9):
        """ Retrieves the result."wait" indicates if you are willing to wait until the measurement
        is over (otherwise, you'll get partial results). "percentage_required" is meaningful only
        when you wait and it indicates the percentage of the allocated probes that have to report
        before the function returns (warning: the measurement may stop even if not enough probes
        reported so you always have to check the actual number of reporting probes in the result). """
        if wait:
            enough = False
            attempts = 0
            results_delay = results_delay_base + (self.num_probes * results_delay_factor)
            maximum_time_for_results = maximum_time_for_results_base + \
                                       (self.num_probes * maximum_time_for_results_factor)
            start = time.time()
            elapsed = 0
            result_data = None
            while not enough and elapsed < maximum_time_for_results:
                if self.notification is not None:
                    self.notification(results_delay)
                time.sleep(results_delay) 
                results_delay *= 2
                request = JsonRequest(self.url_results % self.id)
                attempts += 1
                elapsed = time.time() - start
                try:
                    conn = urllib2.urlopen(request)
                    result_data = json.load(conn) 
                    num_results = len(result_data)
                    if num_results >= self.num_probes*percentage_required:
                        # Requesting a strict equality may be too
                        # strict: if an allocated probe does not
                        # respond, we will have to wait for the stop
                        # of the measurement (many minutes). Anyway,
                        # there is also the problem that a probe may
                        # have sent only a part of its measurements.
                        enough = True
                    else:
                        conn = urllib2.urlopen(JsonRequest(self.url_status % self.id))
                        result_status = json.load(conn) 
                        status = result_status["status"]["name"]
                        if status == "Ongoing":
                            # Wait a bit more
                            pass
                        elif status == "Stopped":
                            enough = True # Even if not enough probes
                        else:
                            raise InternalError("Unexpected status when retrieving the measurement: \"%s\"" % \
                                   result_data["status"])
                    conn.close()
                except urllib2.HTTPError as e:
                    if e.code != 404: # Yes, we may have no result file at
                        # all for some time
                        raise ResultError(str(e.code) + " " + e.reason)
            if result_data is None:
                raise ResultError("No results retrieved")
        else:
            try:
                conn = urllib2.urlopen(request)
                result_data = json.load(conn) 
            except urllib2.HTTPError as e:
                raise ResultError(e.read())
        return result_data
