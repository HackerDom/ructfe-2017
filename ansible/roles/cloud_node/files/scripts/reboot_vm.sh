#!/bin/bash -e

TEAM=${1?Syntax: ./reboot_vm.sh <team_id>}

vm="test_team${TEAM}"

if ! VBoxManage list runningvms | grep -qP "\W${vm}\W"; then
  echo 'msg: ERR, not running'
  exit 1
fi

VBoxManage controlvm "$vm" reset
