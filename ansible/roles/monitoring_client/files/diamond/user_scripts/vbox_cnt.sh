#!/bin/bash

proc="$(pgrep VBoxHeadless | wc -l)"
echo vbox_cnt "${proc}"
