#!/usr/bin/perl

use Mojo::UserAgent;
binmode STDOUT, ':utf8';

my $ua  = Mojo::UserAgent->new;
my $url = 'https://checker:2rZFpTncNN8p9H8wDwP2P2Jww6prcg9k@ructfe.org/checker_json';

my $tx = $ua->get($url);
die %{$tx->error} unless my $res = $tx->success;

my $teams = $res->json;

my $team_id = 0;
for (@$teams) {
  $team_id++;

  my $a   = 60 + int($team_id / 256);
  my $b   = $team_id % 256;
  my $net = "10.$a.$b.0/24";
  my $ip  = "10.$a.$b.2";

  $_->{name} =~ s/'/\\'/;

  print "{name => '$_->{name}', network => '$net', host => '$ip', "
    . "logo => 'https://ructfe.org$_->{logo}', token => '$_->{checker_token}', country => '$_->{country}',";

  if ($team_id > 355) {
    print "bot => [";
    my $bot = [];
    for (1 .. 6) {
      my $sla     = sprintf '%.1f', rand;
      my $attack  = sprintf '%.1f', rand;
      my $defense = sprintf '%.1f', rand;
      print "{sla => $sla, attack => $attack, defense => $defense},";
    }
    print "]";
  }

  print "},\n";
}
