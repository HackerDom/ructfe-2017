#!/bin/bash -e

TEAM=${1?Syntax: ./launch_intra_vpn.sh <team_id>}

cp "/home/cloud/client_intracloud_team${TEAM}.conf" /etc/openvpn/
chown root:root "/etc/openvpn/client_intracloud_team${TEAM}.conf"
systemctl start "openvpn@client_intracloud_team${TEAM}"
