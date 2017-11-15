#!/usr/bin/python3

import sys
import requests
import json
import time
import os
import subprocess
import random
import traceback

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

def log_progress(*params):
    print("progress:", *params, flush=True)

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


def check_vm_exists(vm_name):
    droplets = get_all_vms()
    if droplets is None:
        return None

    for droplet in droplets:
        if droplet["name"] == vm_name:
            return True
    return False


def create_vm(vm_name, attempts=10, timeout=20):
    for i in range(attempts):
        try:
            data = json.dumps({
                "name": vm_name,
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
    return ids

def create_domain_record(name, ip, attempts=10, timeout=20):
    for i in range(attempts):
        try:
            data = json.dumps({
                "type": "A",
                "name": name,
                "data": ip,
                "ttl":1
            })
            resp = requests.post("https://api.digitalocean.com/v2/domains/%s/records" % DOMAIN, headers=HEADERS, data=data)
            if not str(resp.status_code).startswith("2"):
                log_stderr(resp.status_code, resp.headers, resp.text)
                raise Exception("bad status code %d" % resp.status_code)
            return True            
        except Exception as e:
            log_stderr("create_domain_record trying again %s" % (e,))
        time.sleep(timeout)
    return None

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
        if subprocess.call(params, stdout=sys.stderr) == 0:
            return True
        time.sleep(timeout)
    return None

def main():
    net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

    log_progress("0%")
    droplet_id = None
    if net_state == "NOT_STARTED":
        exists = check_vm_exists(VM_NAME)
        if exists is None:
            log_stderr("failed to determine if vm exists, exiting")
            sys.exit(1)

        log_progress("5%")

        if not exists:
            droplet_id = create_vm(VM_NAME)
            if droplet_id is None:
                log_stderr("failed to create vm, exiting")
                sys.exit(1)

        net_state = "DO_LAUNCHED"
        open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)
        time.sleep(1) # this allows to make less requests (there is a limit)

    log_progress("10%")
    ip = None
    if net_state == "DO_LAUNCHED":
        if not droplet_id:
            ip = get_ip_by_vmname(VM_NAME)
        else:
            ip = get_ip_by_id(droplet_id)
        
        if ip is None:
            log_stderr("no ip, exiting")
            sys.exit(1)

        log_progress("15%")

        domain_ids = get_domain_ids_by_hostname(VM_NAME)
        if domain_ids is None:
            log_stderr("failed to check if dns exists, exiting")
            sys.exit(1)
        
        if domain_ids:
            for domain_id in domain_ids:
                delete_domain_record(domain_id)

        log_progress("17%")

        if create_domain_record(VM_NAME, ip):
            net_state = "DNS_REGISTERED"
            open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)
        else:
            log_stderr("failed to create vm: dns register error")
            sys.exit(1)
        
        for i in range(20, 60):
            # just spinning for the sake of smooth progress
            log_progress("%d%%" % i)
            time.sleep(1)

    log_progress("60%")

    if net_state == "DNS_REGISTERED":
        if ip is None:
            ip = get_ip_by_vmname(VM_NAME)

            if ip is None:
                log_stderr("no ip, exiting")
                sys.exit(1)

        log_progress("65%")

        ret = call_unitl_zero_exit(["scp"] + SSH_DO_OPTS + 
            ["db/team%d/server_outside.conf" % TEAM, 
            "%s:/etc/openvpn/server_outside_team%d.conf" % (ip,TEAM)])
        if not ret:
            log_stderr("scp to DO failed")
            sys.exit(1)

        log_progress("70%")

        ret = call_unitl_zero_exit(["scp"] + SSH_DO_OPTS + 
            ["db/team%d/game_network.conf" % TEAM, 
            "%s:/etc/openvpn/game_network_team%d.conf" % (ip,TEAM)])
        if not ret:
            log_stderr("scp to DO failed")
            sys.exit(1)

        log_progress("72%")

        ret = call_unitl_zero_exit(["ssh"] + SSH_DO_OPTS + 
            [ip, "systemctl start openvpn@server_outside_team%d" % TEAM])
        if not ret:
            log_stderr("start internal tun")
            sys.exit(1)

        net_state = "DO_DEPLOYED"
        open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

    log_progress("75%")

    if net_state == "DO_DEPLOYED":
        cloud_ip = get_cloud_ip()
        if not cloud_ip:
            log_stderr("no cloud_ip ip, exiting")
            sys.exit(1)

        log_progress("77%")

        ret = call_unitl_zero_exit(["scp"] + SSH_YA_OPTS + 
            ["db/team%d/client_intracloud.conf" % TEAM,  
            "%s:/home/cloud/client_intracloud_team%d.conf" % (cloud_ip, TEAM)])
        if not ret:
            log_stderr("scp to YA failed")
            sys.exit(1)

        log_progress("78%")

        ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
            [cloud_ip, "sudo", "/cloud/scripts/launch_intra_vpn.sh", str(TEAM)])
        if not ret:
            log_stderr("launch team intra vpn")
            sys.exit(1)
        
        net_state = "READY"
        open("db/team%d/net_deploy_state" % TEAM, "w").write(net_state)

    image_state = open("db/team%d/image_deploy_state" % TEAM).read().strip()
    
    log_progress("80%")

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

            log_progress("85%")

            ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + 
                [cloud_ip, "sudo", "/cloud/scripts/launch_vm.sh", str(TEAM)])
            if not ret:
                log_stderr("launch team vm")
                sys.exit(1)

            image_state = "RUNNING"
            open("db/team%d/image_deploy_state" % TEAM, "w").write(image_state)
    log_progress("100%")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("started: %d" % int(time.time()))
    try:
        main()
    except:
        traceback.print_exc()

    net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()
    image_state = open("db/team%d/image_deploy_state" % TEAM).read().strip()

    log_stderr("NET_STATE:", net_state)
    log_stderr("IMAGE_STATE:", image_state)

    if net_state == "READY" and image_state == "RUNNING":
        print("status: OK")
    elif net_state != "READY":
        print("status: ERR, failed to set up the network")
    elif image_state != "RUNNING":
        print("status: ERR, failed to start up the vm")
    else:
        print("status: ERR")

    print("finished: %d" % int(time.time()))

    sys.exit(0)
