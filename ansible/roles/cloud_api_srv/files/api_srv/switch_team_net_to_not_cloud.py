#!/usr/bin/python3

import sys
import requests
import json
import time
import os
import subprocess
import random

from do_token import TOKEN

ROUTER_HOST = "router2.ructfe.clients.haas.yandex.net" # change me before the game

TEAM = int(sys.argv[1])
VM_NAME = "router-team%d" % TEAM

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer %s" % TOKEN,
}

SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no", 
    "-o", "CheckHostIP=no", 
    "-o", "NoHostAuthenticationForLocalhost=yes",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=10"
]

SSH_YA_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2017_ya_deploy"
]

SSH_DO_OPTS = SSH_OPTS + [
    "-o", "User=root",
    "-o", "IdentityFile=ructf2017_do_deploy"
]

def get_all_vms(attempts=5, timeout=10):
    vms = {}
    url = "https://api.digitalocean.com/v2/droplets?per_page=200"
    
    cur_attempt = 1

    while True:
        try:
            resp = requests.get(url, headers=HEADERS)
            if not str(resp.status_code).startswith("2"):
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)

            data = json.loads(resp.text)

            for droplet in data["droplets"]:
                vms[droplet["id"]] = droplet

            if "links" in data and "pages" in data["links"] and "next" in data["links"]["pages"]:
                url = data["links"]["pages"]["next"]
            else:
                break

        except Exception as e:
            log_stderr("get_all_vms trying again %s" % (e,))
            cur_attempt += 1
            if cur_attempt > attempts:
                return None # do not return parts of the output
            time.sleep(timeout)
    return list(vms.values())

def get_ip_by_id(droplet_id, attempts=5, timeout=20):
    for i in range(attempts):
        try:
            resp = requests.get("https://api.digitalocean.com/v2/droplets/%d" % droplet_id, headers=HEADERS)
            data = json.loads(resp.text)

            return data['droplet']['networks']['v4'][0]['ip_address']
        except Exception as e:
            log_stderr("get_ip_by_id trying again %s" % (e,))
        time.sleep(timeout)
    log_stderr("failed to get ip by id")
    return None

def get_ip_by_vmname(vm_name):
    ids = set()

    droplets = get_all_vms()
    if droplets is None:
        return None

    for droplet in droplets:
        if droplet["name"] == vm_name:
            ids.add(droplet['id'])

    if len(ids) > 1:
        log_stderr("warning: there are more than one droplet with name %s, using random :)" % vm_name)

    if not ids:
        return None

    return get_ip_by_id(list(ids)[0])

def log_stderr(*params):
    print("Team %d:" % TEAM, *params,file=sys.stderr)

def call_unitl_zero_exit(params, attempts=60, timeout=10):
    for i in range(attempts):
        if subprocess.call(params) == 0:
            return True
        time.sleep(timeout)
    return None

os.chdir(os.path.dirname(os.path.realpath(__file__)))

net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

droplet_id = None
if net_state != "READY":
    log_stderr("the network state should be READY")
    sys.exit(1)

team_state = open("db/team%d/team_state" % TEAM).read().strip()

ip = None

if team_state == "CLOUD":
    ip = get_ip_by_vmname(VM_NAME)
    if ip is None:
        log_stderr("no ip, exiting")
        sys.exit(1)

    ret = call_unitl_zero_exit(["ssh"] + SSH_DO_OPTS + 
        [ip, "systemctl stop openvpn@game_network_team%d" % TEAM])
    if not ret:
        log_stderr("stop main game net tun")
        sys.exit(1)

    team_state = "MIDDLE_STATE"
    open("db/team%d/team_state" % TEAM, "w").write(team_state)

if team_state == "MIDDLE_STATE":
    if ip is None:
        ip = get_ip_by_vmname(VM_NAME)
        if ip is None:
            log_stderr("no ip, exiting")
            sys.exit(1)

    ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
        [ROUTER_HOST, "sudo", "/root/cloud/switch_team_to_not_cloud.sh", str(TEAM), ip])
    if not ret:
        log_stderr("switch_team_to_not_cloud")
        sys.exit(1)

    team_state = "NOT_CLOUD"
    open("db/team%d/team_state" % TEAM, "w").write(team_state)

print("TEAM_STATE:", team_state)
sys.exit(0)
