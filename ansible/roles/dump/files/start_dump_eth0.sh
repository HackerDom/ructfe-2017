#!/bin/bash

exec tcpdump -U -i eth0 -C 20 -w "/home/dump/dump" -s 0
