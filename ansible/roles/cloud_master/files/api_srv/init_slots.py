#!/usr/bin/python3

import sys
import os

CLOUD_PHYS_SERVERS = [
    ("5.45.248.218", "cld0"),
]

VM_PER_SERVER = 30

if __name__ != "__main__":
    raise Exception("I am not a module")

os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    os.mkdir("slots")
except FileExistsError:
    print("Remove ./slots dir first")
    sys.exit(1)


for num in range(len(CLOUD_PHYS_SERVERS) * VM_PER_SERVER):
    cur_srv_ip, cur_srv_name = CLOUD_PHYS_SERVERS[num % len(CLOUD_PHYS_SERVERS)]
    file_name = "slot_%04d_%s" % (num, cur_srv_name)
    open("slots/%s" % file_name, "w").write(cur_srv_ip + "\n")
