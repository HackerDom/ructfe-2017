#!/bin/bash

TEAM=${1?Syntax: ./attach_vm_gui.sh <team_id> [fix]}
FIX=${2}

vm="test_team${TEAM}"

# fix keyboard layout
if [ "$FIX" == fix ]; then
 echo fixing
 setxkbmap us -print | xkbcomp - $DISPLAY
fi

VirtualBox --startvm "$vm" --separate
