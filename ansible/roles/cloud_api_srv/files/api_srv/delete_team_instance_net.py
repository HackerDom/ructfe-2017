#!/usr/bin/python3

import sys
import requests
import json
import time
import os
import subprocess

from do_token import TOKEN

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

SSH_YA_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2017_ya_deploy"
]


def log_stderr(*params):
    print("Team %d:" % TEAM, *params,file=sys.stderr)

def delete_vm_by_id(droplet_id, attempts=10, timeout=20):
    for i in range(attempts):
        try:
            log_stderr("deleting droplet")
            resp = requests.delete("https://api.digitalocean.com/v2/droplets/%d" % droplet_id, headers=HEADERS)
            if not str(resp.status_code).startswith("2"):
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)
            return True
        except Exception as e:
            log_stderr("delete_vm_by_id trying again %s" % (e,))
        time.sleep(timeout)
    return False


def get_all_vms(attempts=5, timeout=20):
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


def get_ids_by_vmname(vm_name):
    ids = set()

    droplets = get_all_vms()
    if droplets is None:
        return None

    for droplet in droplets:
        if droplet["name"] == vm_name:
            ids.add(droplet['id'])
    return ids

def get_all_domain_records(attempts=5, timeout=20):
    records = {}
    url = "https://api.digitalocean.com/v2/domains/%s/records?per_page=200" % DOMAIN
    
    cur_attempt = 1

    while True:
        try:
            resp = requests.get(url, headers=HEADERS)
            if not str(resp.status_code).startswith("2"):
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)

            data = json.loads(resp.text)
            for record in data["domain_records"]:
                records[record["id"]] = record

            if "links" in data and "pages" in data["links"] and "next" in data["links"]["pages"]:
                url = data["links"]["pages"]["next"]
            else:
                break
        except Exception as e:
            log_stderr("get_all_domain_records trying again %s" % (e,))
            cur_attempt += 1
            if cur_attempt > attempts:
                return None # do not return parts of the output
            time.sleep(timeout)

    return list(records.values())


def get_domain_ids_by_hostname(host_name):
    ids = set()

    records = get_all_domain_records()
    if records is None:
        return None

    for record in records:
        if record["type"] == "A" and record["name"] == host_name:
            ids.add(record['id'])
            
    if not ids:
        log_stderr("failed to get domain ids by hostname")
    return ids

def get_cloud_ip():
    return open("db/team%d/cloud_ip" % TEAM).read().strip()

def delete_domain_record(domain_id, attempts=10, timeout=20):
    for i in range(attempts):
        try:
            log_stderr("deleting domain record %d" % domain_id)
            resp = requests.delete("https://api.digitalocean.com/v2/domains/%s/records/%d" % (DOMAIN, domain_id), headers=HEADERS)
            if not str(resp.status_code).startswith("2"):
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)
            return True
        except Exception as e:
            log_stderr("delete_domain_record trying again %s" % (e,))
        time.sleep(timeout)
    return False

def call_unitl_zero_exit(params, attempts=60, timeout=10):
    for i in range(attempts):
        if subprocess.call(params) == 0:
            return True
        time.sleep(timeout)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

droplet_id = None
if net_state == "READY":
    cloud_ip = get_cloud_ip()
    if not cloud_ip:
        log_stderr("no cloud ip, exiting")
        sys.exit(1)

    ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
        [cloud_ip, "sudo", "/cloud/scripts/remove_intra_vpn.sh", str(TEAM)])
    if not ret:
        log_stderr("remove team intra vpn failed")
        sys.exit(1)
    
    net_state = "DO_DEPLOYED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

if net_state == "DO_DEPLOYED":
    net_state = "DNS_REGISTERED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

if net_state == "DNS_REGISTERED":
    domain_ids = get_domain_ids_by_hostname(VM_NAME)
    if domain_ids is None:
        log_stderr("failed to get domain ids, exiting")
        sys.exit(1)

    for domain_id in domain_ids:
        if not delete_domain_record(domain_id):
            log_stderr("failed to delete domain %d, exiting" % domain_id)
            sys.exit(1)

    net_state = "DO_LAUNCHED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

if net_state == "DO_LAUNCHED":
    do_ids = get_ids_by_vmname(VM_NAME)
    
    if do_ids is None:
        log_stderr("failed to get vm ids, exiting")
        sys.exit(1)

    if len(do_ids) > 1:
        log_stderr("warinig: more than 1 droplet to be deleted")

    for do_id in do_ids:
        if not delete_vm_by_id(do_id):
            log_stderr("failed to delete droplet %d, exiting" % do_id)
            sys.exit(1)

    net_state = "NOT_STARTED"
    open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

print("NET_STATE:", net_state)
sys.exit(0)
