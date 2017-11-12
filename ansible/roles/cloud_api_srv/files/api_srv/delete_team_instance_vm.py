#!/usr/bin/python3

import sys
import requests
import json
import time
import os
import subprocess
import random

TEAM = int(sys.argv[1])
VM_NAME = "router-team%d" % TEAM

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no", 
    "-o", "CheckHostIP=no", 
    "-o", "NoHostAuthenticationForLocalhost=yes",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "UserKnownHostsFile=/dev/null"
]

SSH_YA_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2017_ya_deploy"
]


def log_stderr(*params):
    print("Team %d:" % TEAM, *params,file=sys.stderr)

def get_cloud_ip():
    return open("db/team%d/cloud_ip" % TEAM).read().strip()

def call_unitl_zero_exit(params, attempts=60, timeout=10):
    for i in range(attempts):
        if subprocess.call(params) == 0:
            return True
        time.sleep(timeout)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

image_state = open("db/team%d/image_deploy_state" % TEAM).read().strip()

if image_state == "RUNNING":
    cloud_ip = get_cloud_ip()
    if not cloud_ip:
        log_stderr("no cloud_ip ip, exiting")
        sys.exit(1)

    ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
          [cloud_ip, "sudo", "/cloud/scripts/remove_vm.sh", str(TEAM)])
    if not ret:
        log_stderr("failed to remove team vm")
        sys.exit(1)
    image_state = "NOT_STARTED"
    open("db/team%d/image_deploy_state" % TEAM, "w").write(image_state)

# print("NET_STATE:", net_state)
print("IMAGE_STATE:", image_state)
sys.exit(0)
