#!/usr/bin/python3

import sys
import requests
import json
import time
import os
import subprocess
import random

from do_token import TOKEN

CLOUD_HOSTS = ["5.45.248.218"]

TEAM = int(sys.argv[1])
VM_NAME = "router-team%d" % TEAM

DOMAIN = "cloud.alexbers.com"

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
    "-o", "UserKnownHostsFile=/dev/null"
]

SSH_DO_OPTS = SSH_OPTS + [
    "-o", "User=root",
    "-o", "IdentityFile=ructf2017_do_deploy"
]

SSH_YA_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2017_ya_deploy"
]


def log_stderr(*params):
    print("Team %d:" % TEAM, *params,file=sys.stderr)

def check_vm_exists():
    resp = requests.get("https://api.digitalocean.com/v2/droplets", headers=HEADERS)
    data = json.loads(resp.text)

    for droplet in data["droplets"]:
        if droplet["name"] == VM_NAME:
            return True
    return False


def create_vm(attempts=10, timeout=20):
    for i in range(attempts):
        try:
            data = json.dumps({
                "name": VM_NAME,
                "region": "ams2",
                "size": "512mb",
                "image": 29261612,
                "ssh_keys": [435386,15240256],
                "backups": False,
                "ipv6": False,
                "user_data": "#!/bin/bash\n\n",
                "private_networking": None,
                "volumes": None,
                "tags": []  # tags are too unstable in DO
            })

            log_stderr("creating new")
            resp = requests.post("https://api.digitalocean.com/v2/droplets", headers=HEADERS, data=data)
            if resp.status_code not in [200, 201, 202]:
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)

            droplet_id = json.loads(resp.text)["droplet"]["id"]
            return droplet_id
        except Exception as e:
            log_stderr("create_vm trying again %s" % (e,))
        time.sleep(timeout)
    return None
        

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
    return ""

def get_ip_by_vmname(team, attempts=5, timeout=20):
    for i in range(attempts):
        try:
            resp = requests.get("https://api.digitalocean.com/v2/droplets", headers=HEADERS)
            data = json.loads(resp.text)
            print(data)

            for droplet in data["droplets"]:
                if droplet["name"] == VM_NAME:
                    return droplet['networks']['v4'][0]['ip_address']
            raise Exception("no droplet with such name")
        except Exception as e:
            log_stderr("get_ip_by_vmname trying again %s" % (e,))
        time.sleep(timeout)
    log_stderr("failed to get ip by vmname")
    return ""

def gen_cloud_ip():
    cloud_ip = random.choice(CLOUD_HOSTS)
    return cloud_ip

def get_cloud_ip():
    try:
        return open("db/team%d/cloud_ip" % TEAM).read().strip()
    except FileNotFoundError as e:
        cloud_ip = gen_cloud_ip()
        log_stderr("Generating cloud_ip, assigned %s" % cloud_ip)
        open("db/team%d/cloud_ip" % TEAM, "w").write(cloud_ip)
        return cloud_ip

def create_domain_record(name, ip):
    data = json.dumps({
        "type": "A",
        "name": name,
        "data": ip,
        "ttl":1
    })
    resp = requests.post("https://api.digitalocean.com/v2/domains/%s/records" % DOMAIN, headers=HEADERS, data=data)
    return resp.status_code in [200, 201, 202]

def call_unitl_zero_exit(params, attempts=60, timeout=10):
    for i in range(attempts):
        if subprocess.call(params) == 0:
            return True
        time.sleep(timeout)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

droplet_id = None
if net_state == "NOT_STARTED":
    if not check_vm_exists():
        droplet_id = create_vm()
        if not droplet_id:
            log_stderr("failed to create vm, exiting")
            sys.exit(1)

    net_state = "DO_LAUNCHED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)
    time.sleep(1) # this allows to make less requests (there is a limit)

ip = None
if net_state == "DO_LAUNCHED":
    if not droplet_id:
        ip = get_ip_by_vmname(VM_NAME)
    else:
        ip = get_ip_by_id(droplet_id)
    if not ip:
        log_stderr("no ip, exiting")
        sys.exit(1)

    if create_domain_record(VM_NAME, ip):
        net_state = "DNS_REGISTERED"
        open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)
    else:
        log_stderr("failed to create vm: dns register error")
        sys.exit(1)

if net_state == "DNS_REGISTERED":
    if not ip:
        ip = get_ip_by_vmname(VM_NAME)
    if not ip:
        log_stderr("no ip, exiting")
        sys.exit(1)

    ret = call_unitl_zero_exit(["scp"] + SSH_DO_OPTS + 
        ["db/team%d/server_outside.conf" % TEAM, 
        "%s:/etc/openvpn/server_outside_team%d.conf" % (ip,TEAM)])
    if not ret:
        log_stderr("scp to DO failed")
        sys.exit(1)
    ret = call_unitl_zero_exit(["scp"] + SSH_DO_OPTS + 
        ["db/team%d/game_network.conf" % TEAM, 
        "%s:/etc/openvpn/game_network_team%d.conf" % (ip,TEAM)])
    if not ret:
        log_stderr("scp to DO failed")
        sys.exit(1)
    ret = call_unitl_zero_exit(["ssh"] + SSH_DO_OPTS + 
        [ip, "systemctl start openvpn@server_outside_team%d" % TEAM])
    if not ret:
        log_stderr("start internal tun")
        sys.exit(1)

    net_state = "DO_DEPLOYED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

if net_state == "DO_DEPLOYED":
    cloud_ip = get_cloud_ip()
    if not cloud_ip:
        log_stderr("no cloud_ip ip, exiting")
        sys.exit(1)

    ret = call_unitl_zero_exit(["scp"] + SSH_YA_OPTS + 
        ["db/team%d/client_intracloud.conf" % TEAM,  
        "%s:/home/cloud/client_intracloud_team%d.conf" % (cloud_ip, TEAM)])
    if not ret:
        log_stderr("scp to YA failed")
        sys.exit(1)

    ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
        [cloud_ip, "sudo", "/cloud/scripts/launch_intra_vpn.sh", str(TEAM)])
    if not ret:
        log_stderr("launch team intra vpn")
        sys.exit(1)
    
    net_state = "READY"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

image_state = open("db/team%d/image_deploy_state" % TEAM).read().strip()

if net_state == "READY":
    if image_state == "NOT_STARTED":
        cloud_ip = get_cloud_ip()

        if not cloud_ip:
            log_stderr("no cloud_ip ip, exiting")
            sys.exit(1)

        ret = call_unitl_zero_exit(["scp"] + SSH_YA_OPTS + 
            ["db/team%d/root_passwd_hash.txt" % TEAM,  
            "%s:/home/cloud/root_passwd_hash_team%d.txt" % (cloud_ip, TEAM)])
        if not ret:
            log_stderr("scp to YA failed")
            sys.exit(1)

        ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
            [cloud_ip, "sudo", "/cloud/scripts/launch_vm.sh", str(TEAM)])
        if not ret:
            log_stderr("launch team vm")
            sys.exit(1)

        image_state = "RUNNING"
        open("db/team%d/image_deploy_state" % TEAM, "w").write(image_state)

print("NET_STATE:", net_state)
print("IMAGE_STATE:", image_state)
sys.exit(0)
