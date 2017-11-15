#!/usr/bin/python3

import sys
import json
import time
import os
import traceback

import do_api
from cloud_common import (get_cloud_ip, log_progress, call_unitl_zero_exit, 
                          SSH_OPTS, SSH_DO_OPTS, SSH_YA_OPTS, DOMAIN)

TEAM = int(sys.argv[1])
VM_NAME = "router-team%d" % TEAM

DO_IMAGE = 29261612
DO_SSH_KEYS = [435386,15240256]


def log_stderr(*params):
    print("Team %d:" % TEAM, *params,file=sys.stderr)


def main():
    net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

    log_progress("0%")
    droplet_id = None
    if net_state == "NOT_STARTED":
        exists = do_api.check_vm_exists(VM_NAME)
        if exists is None:
            log_stderr("failed to determine if vm exists, exiting")
            sys.exit(1)

        log_progress("5%")

        if not exists:
            droplet_id = do_api.create_vm(VM_NAME, image=DO_IMAGE, ssh_keys=DO_SSH_KEYS)
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
            ip = do_api.get_ip_by_vmname(VM_NAME)
        else:
            ip = do_api.get_ip_by_id(droplet_id)
        
        if ip is None:
            log_stderr("no ip, exiting")
            sys.exit(1)

        log_progress("15%")

        domain_ids = do_api.get_domain_ids_by_hostname(VM_NAME, DOMAIN)
        if domain_ids is None:
            log_stderr("failed to check if dns exists, exiting")
            sys.exit(1)
        
        if domain_ids:
            for domain_id in domain_ids:
                do_api.delete_domain_record(domain_id, DOMAIN)

        log_progress("17%")

        if do_api.create_domain_record(VM_NAME, ip, DOMAIN):
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
            ip = do_api.get_ip_by_vmname(VM_NAME)

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
        cloud_ip = get_cloud_ip(TEAM, may_generate=True)
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
            cloud_ip = get_cloud_ip(TEAM)

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
