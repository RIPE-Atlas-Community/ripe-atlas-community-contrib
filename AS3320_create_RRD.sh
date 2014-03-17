### change to the script directory
#
# creates the RRD file needed for the example:
# retrieve+icmp+periodically+with+crontab+and+write+to+rrd.py
#
# Based on https://calomel.org/rrdtool.html tutorial and graph examples
#
# Daniel Gomez <daniel.gomez@synaix.de>
#
cd /home/user0/ripeatlas/

rrdtool create AS3320_latency_db.rrd \
--step 300 \
DS:plAS3320:GAUGE:600:0:100 \
DS:rttAS3320:GAUGE:600:0:10000000 \
RRA:AVERAGE:0.5:1:86400 \
