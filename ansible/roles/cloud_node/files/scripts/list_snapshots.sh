#!/bin/bash -e

TEAM=${1?Syntax: ./list_snapshots.sh <team_id>}

vm="test_team${TEAM}"

VBoxManage snapshot "$vm" list || true
