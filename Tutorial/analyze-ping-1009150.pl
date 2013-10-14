#!/usr/bin/env perl

# usage :
# $0 [-v]

use Modern::Perl;     # enable stricture and features like "say"
use WWW::Mechanize;   # programmatic web browser
use File::Slurp;      # Simple and Efficient Reading/Writing/Modifying of Complete Files'
use JSON::XS;         # Written in C, faster than JSON::PP

my $measurement = 1009150;
my $url = "http://atlas.ripe.net/api/v1/measurement/$measurement/result/";
my $file = "$measurement.json";
my $count_probes =
my $count_probe_unsucess = 0;
my ($raw_content, @non_success_probes);

unless (-s $file) {
    my $b = WWW::Mechanize->new(autocheck => 1);
    $b->get($url, ':content_file' => $file );
}

if (-s $file) {
    $raw_content = read_file $file;
}
else {
    warn "Error: no files [$file] mech fails to download it\n";
}

# Dereference of the JSON data structure in a perl array of hashes
my @arr_of_hashes = @{ decode_json $raw_content };

# Dump JSON data structure to STDOUT if -v arg is provided
do {
    use Data::Dumper;
    print Dumper \@arr_of_hashes;
    exit(0);
} if @ARGV ~~ m/-v/;

# Using a "label", it's easy to move on the next probe using 
# "next PROBE"
PROBE: foreach my $hash_probe (@arr_of_hashes) {
    if (ref $hash_probe eq 'HASH') {
        # prb_id = a probe ID
        if (exists $hash_probe->{"prb_id"}) {
            $count_probes++;
            if (exists $hash_probe->{"result"}) {
                foreach my $h (@{ $hash_probe->{"result"} }) {
                    # rtt = Round Trip Time
                    unless (exists $h->{"rtt"}) {
                        push @non_success_probes, $hash_probe->{'prb_id'};
                        $count_probe_unsucess++;
                        next PROBE;
                    }
                }
            }
            else {
                warn "Error: probe [$hash_probe->{'prb_id'}] exists but no result HASH\n";
            }
        }
    }
    else {
        warn "Not a HASH element :/\n";
    }
}

say "non success probes: \n\t", join "\n\t", @non_success_probes;

print <<EOF
$count_probes probes counted
$count_probe_unsucess non success probes
EOF
