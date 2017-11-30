#!/bin/bash

exec tcpdump -U -i eth1 -C 20 -w "/home/dump/dump" -s 0
