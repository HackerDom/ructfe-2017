#!/usr/bin/python3

import sys
import time
import os
import traceback

import do_api
from cloud_common import (get_cloud_ip, log_progress, call_unitl_zero_exit,
                          SSH_OPTS, SSH_DO_OPTS, SSH_YA_OPTS, ROUTER_HOST)

TEAM = int(sys.argv[1])
VM_NAME = "router-team%d" % TEAM


def log_stderr(*params):
    print("Team %d:" % TEAM, *params, file=sys.stderr)


def main():
    net_state = open("db/team%d/net_deploy_state" % TEAM).read().strip()

    droplet_id = None
    if net_state != "READY":
        log_stderr("the network state should be READY")
        sys.exit(1)

    team_state = open("db/team%d/team_state" % TEAM).read().strip()

    ip = None

    if team_state == "CLOUD":
        ip = do_api.get_ip_by_vmname(VM_NAME)
        if ip is None:
            log_stderr("no ip, exiting")
            sys.exit(1)

        cmd = ["systemctl stop openvpn@game_network_team%d" % TEAM]
        ret = call_unitl_zero_exit(["ssh"] + SSH_DO_OPTS + [ip] + cmd)
        if not ret:
            log_stderr("stop main game net tun")
            sys.exit(1)

        team_state = "MIDDLE_STATE"
        open("db/team%d/team_state" % TEAM, "w").write(team_state)

    if team_state == "MIDDLE_STATE":
        if ip is None:
            ip = do_api.get_ip_by_vmname(VM_NAME)
            if ip is None:
                log_stderr("no ip, exiting")
                sys.exit(1)

        cmd = ["sudo", "/root/cloud/switch_team_to_not_cloud.sh",
               str(TEAM), ip]
        ret = call_unitl_zero_exit(["ssh"] + SSH_YA_OPTS + [ROUTER_HOST] + cmd)
        if not ret:
            log_stderr("switch_team_to_not_cloud")
            sys.exit(1)

        team_state = "NOT_CLOUD"
        open("db/team%d/team_state" % TEAM, "w").write(team_state)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("started: %d" % int(time.time()))
    try:
        main()
    except:
        traceback.print_exc()

    team_state = open("db/team%d/team_state" % TEAM).read().strip()

    log_stderr("TEAM_STATE:", team_state)

    if team_state == "NOT_CLOUD":
        print("status: OK")
    else:
        print("status: ERR")

    print("finished: %d" % int(time.time()))

    sys.exit(0)
