#!/bin/bash
# 
# roundtriptime_graph.sh creates a PNG File for the example:
# retrieve+icmp+periodically+with+crontab+and+write+to+rrd.py
# 
# Based on https://calomel.org/rrdtool.html tutorial and graph examples 
#
# Daniel Gomez <daniel.gomez@synaix.de> 
#

## change directory to the rrdtool script dir
cd /home/user0/ripeatlas
 
## Graph for last 24 hours 
/usr/bin/rrdtool graph roundtriptime_graph.png -w 785 -h 120 -a PNG -E --start -86400 --end now \
--font DEFAULT:7: \
--title "Ping" \
--watermark "`date`" \
--vertical-label "latency(ms)" \
--right-axis-label "latency(ms)" \
--lower-limit 0 \
--right-axis 1:0 \
--x-grid MINUTE:15:HOUR:1:MINUTE:120:0:%R \
--alt-y-grid --rigid \
DEF:roundtripAS3320=AS3320_latency_db.rrd:rttAS3320:AVERAGE \
LINE1:roundtripAS3320#FF8C00:"D-Telekom(ms)" \
GPRINT:roundtripAS3320:LAST:"Cur\: %5.2lf" \
GPRINT:roundtripAS3320:AVERAGE:"Avg\: %5.2lf" \
GPRINT:roundtripAS3320:MAX:"Max\: %5.2lf" \
GPRINT:roundtripAS3320:MIN:"Min\: %5.2lf\t\t\t" \
COMMENT:"AS number\:AS3320" \
COMMENT:"\s" \
COMMENT:"\s" \

## copy to the web directory
cp roundtriptime_graph.png /var/www/
