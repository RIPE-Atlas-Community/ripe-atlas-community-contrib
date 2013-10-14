#!/usr/bin/env perl

use Modern::Perl;
use JSON;
use LWP::UserAgent;

my $api_key = 'xxx';

# Perl Data Structure of the futur JSON
my $perl_DS_IN = {
    'probes' => [
        {
            'value'     => 'PT',
            'requested' => 9,
            'type'      => 'country'
        }
    ],
    'definitions' => [
        {
            'is_oneoff'     => JSON::true,
            'target'        => '212.27.54.252',
            'af'            => 4,
            'type'          => 'ping',
            'description'   => 'Ping Free ISP DNS server'
        }
    ]
};

# the Perl DS become a JSON DS
my $js = encode_json $perl_DS_IN;
my $url = "https://atlas.ripe.net/api/v1/measurement/?key=$api_key";
my $ua = LWP::UserAgent->new;
my $req = HTTP::Request->new(POST => $url);
$req->content_type('application/json');
$req->header(Accept => 'application/json');
$req->content($js);
my $res = $ua->request($req);
my $json_out;
if ($res->is_success) {
    $json_out = $res->content;
}
else {
    die $res->status_line, $res->content;
}

my $perl_DS_OUT = decode_json $json_out;
my @measurements = @{ $perl_DS_OUT->{'measurements'} };
say "http://atlas.ripe.net/api/v1/measurement/$measurements[0]/result/ measurement started";
