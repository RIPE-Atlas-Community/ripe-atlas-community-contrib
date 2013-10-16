#!/bin/sh

# Alessandro alessandro.improta(at)iit.cnr.it

# Warning: this solution is brittle, since any change in the JSON
# formatting can break them.

sed s/"addr"/"\naddr"/g results.json | grep result | grep -v "rtt" | uniq | wc -l

# Explanations: first, we split the json file in lines, by considering that each
# result has to begin with the keyword "result".

# Then we get rid of those lines that do not contain a result.

# Then, we consider only those lines that contain do not contain even
# a rtt and we count them. I used also "uniq" to avoid duplicates

# To get the probes IDs: like before, but now we just list the probe
# IDs (no duplicates)

sed s/"addr"/"\naddr"/g results.json | grep result | grep -v "rtt" | sed s/"prb_id"/"\nprb_id"/g | grep "prb_id" | sed s/"prb_id\"\:"// | awk -F "," '{print $1}' | uniq


