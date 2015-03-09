#!/usr/bin/perl

use strict;
use warnings;

use Data::Dumper;
use Net::DNS::Resolver;
use List::Util qw(sum);

use lib "/opt/local/lib/perl5/vendor_perl/5.16.3";
use JSON;

# Description: script for printing traceroute results from ATLAS in pretty form
# Author: Pavel Odintsov
# Email: pavel.odintsov@gmail.com
# How to install JSON module on MAC OS X? sudo port install p5-json 

sub get_reverse {
    my $ip = shift;
  
    unless ($ip) {
        return '';
    }

    my $res = Net::DNS::Resolver->new;

    # Prevent hungup on DNS resolve
    $res->tcp_timeout( 1 );
    $res->udp_timeout( 1 );

    # create the reverse lookup DNS name (note that the octets in the IP address need to be reversed).
    my $reversed_ip = join '.', reverse split(/\./, $ip);
    my $target_IP = "$reversed_ip.in-addr.arpa";

    my $query = $res->query("$target_IP", "PTR");

    if ($query) {
        foreach my $rr ($query->answer) {
    	    unless ($rr->type eq "PTR") {
                next;
	    }
    	    return $rr->rdatastr;
  	}
    } else {
        return '';
    }
}

if (scalar @ARGV == 0) {
    print "Please provide path to file with json data from ATLAS\n";
    exit 1;
}

open my $fl, "<", $ARGV[0] or die "Can't open file $ARGV[0]";
my $data = join '', <$fl>;

my $decoded = decode_json($data);

my $measures_sorted_by_probe_id = {};
for my $measure (@$decoded) {
    push @{ $measures_sorted_by_probe_id->{ $measure->{prb_id} } }, $measure;  
}

for my $probe_id (keys %$measures_sorted_by_probe_id) {
    print "Probe ID: $probe_id\n\n";
    for my $measure (@{$measures_sorted_by_probe_id->{$probe_id}}) {
        my @hops = @{ $measure->{result} };
 
        my $pretty_timestamp = localtime($measure->{timestamp});
        print "Traceroute measure executed from $measure->{src_addr} to $measure->{dst_addr} at $pretty_timestamp\n"; 

        # print Dumper($measure);
        # exit 1;

        for my $hop (@hops) {
	    #print Dumper $hop;
            my $first_try = $hop->{result}->[0];
            my $this_request_failed = $first_try->{x} && $first_try->{x} eq '*'; 

            if ($this_request_failed) {
                print " $hop->{hop} *\n";
                next;
            }
 
            my $average_rtt = 0;

            if (ref $hop->{result} eq 'ARRAY' && scalar @{ $hop->{result} } > 0 && !$this_request_failed) {
                my @rtts = ();
                for my $tracrouter_retry (@{ $hop->{result} }) {
                    # Filter out only defined entries
                    if ($tracrouter_retry->{rtt}) {
                        push @rtts, $tracrouter_retry->{rtt};
                    }
                }

                # print Dumper(\@rtts);

                if (scalar @rtts > 0) {
                    $average_rtt = sum(@rtts) / scalar @rtts;
                    # Round by 3 digits after point 
                    $average_rtt = sprintf("%.3f", $average_rtt);
                }
            }

            #print Dumper($first_try);
            my $reverse = get_reverse($first_try->{from});

            unless ($reverse) {
                $reverse = $first_try->{from};
            }

            print " $hop->{hop} $reverse ($first_try->{from}) $average_rtt ms\n";
        }

        print "\n\n";  
    }
}
