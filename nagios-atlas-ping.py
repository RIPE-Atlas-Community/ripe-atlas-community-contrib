#!/usr/bin/python
"""Nagios ping check using RIPE Atlas."""
import RIPEAtlas
import argparse
import nagiosplugin

class Measurement(nagiosplugin.Resource):
  def __init__(self, target, ip_version, probes, key):
    self.target = target
    self.ip_version = ip_version
    self.probes = probes
    self.key = key

  def probe(self):
    data = { "definitions": [ { "target": self.target,
                                "af": self.ip_version,
                                "resolve_on_probe": True,
                                "description": "Nagios ping check: %s" % self.target,
                                "type": "ping",
                                "is_oneoff": True } ],
             "probes": [ { "requested": max([int(self.probes * 0.3), 1]),
                           "type": "area",
                           "value": "West" },
                         { "requested": max([int(self.probes * 0.3), 1]),
                           "type": "area",
                           "value": "North-Central" },
                         { "requested": max([int(self.probes * 0.05), 1]),
                           "type": "area",
                           "value": "South-Central" },
                         { "requested": max([int(self.probes * 0.15), 1]),
                           "type": "area",
                           "value": "North-East" },
                         { "requested": max([int(self.probes * 0.2), 1]),
                           "type": "area",
                           "value": "South-East" } ] }
    measurement = RIPEAtlas.Measurement(data, key=self.key)
    results = measurement.results(wait=True, percentage_required=0.5)
    if (results):
      failed = [result for result in results if result["rcvd"] < result["sent"]]
      yield nagiosplugin.Metric("failed", len(failed), context="failed")

@nagiosplugin.guarded
def main():
  argp = argparse.ArgumentParser(description=__doc__)
  argp.add_argument("-w", "--warning", default="25", metavar="RANGE", help="Return warning if results within RANGE have failed")
  argp.add_argument("-c", "--critical", default="50", metavar="RANGE", help="Return critical if results within RANGE have failed")
  argp.add_argument("-t", "--target", required=True, help="Target hostname")
  argp.add_argument("-p", "--probes", default=100, type=int, help="How many probes to use")
  argp.add_argument("-6", "--ipv6", action='store_true', help="Use IPv6")
  argp.add_argument("-k", "--key", required=True, help="API key")
  args = argp.parse_args()

  check = nagiosplugin.Check(Measurement(args.target, 6 if args.ipv6 else 4, args.probes, args.key),
                             nagiosplugin.ScalarContext("failed", args.warning, args.critical, fmt_metric="{value} failed results from probes"))
  check.main(timeout=900)

if __name__ == '__main__':
  main()
