#!/bin/bash

myprint="console.log"
myjs="/usr/bin/node"
myjson="1009150.json"

"$myjs"<<!
/*

   Using Unix-like shell (for the here-doc) + javascript, just for fun =)

   To run the script (Debian or Debian likes) :
   % sudo apt-get install nodejs # or rhino
   % chmod +x exercice-ping-1009150-js.sh
   % ./exercice-ping-1009150-js.sh

   This script can be run with rhino instead of nodejs with some few changes.

*/

var timeouts = 0
var errors = 0
var num_rtt = 0
var total_rtt = 0 

// Hack to read the whole JSON data structure
// in a JS var from within the shell :
var results = $(< $myjson)

for (var k in results) {
    var h = results[k]
    for (test in h.result) {
        var z = h.result[test]
        if (typeof z.x !== "undefined") {
            timeouts += 1
        }
        else if (typeof z.error !== "undefined") {
            errors += 1
        }
        else if (typeof z.rtt !== "undefined") {
            num_rtt += 1
            total_rtt += z.rtt
        }
    }
}
$myprint(
    results.length + " results, " + timeouts + " timeouts, " + errors +
    " errors, average RTT " + Number(total_rtt/num_rtt).toFixed(2) + " ms"
)
!
