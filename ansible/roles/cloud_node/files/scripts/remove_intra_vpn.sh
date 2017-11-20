#!/bin/bash -e

TEAM=${1?Syntax: ./remove_intra_vpn.sh <team_id>}

rm "/etc/openvpn/client_intracloud_team${TEAM}.conf" || true
systemctl stop "openvpn@client_intracloud_team${TEAM}"
