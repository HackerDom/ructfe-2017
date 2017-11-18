import subprocess
import sys
import time
import random

DOMAIN = "cloud.alexbers.com"

CLOUD_HOSTS = ["5.45.248.218"]

# change me before the game
ROUTER_HOST = "router2.ructfe.clients.haas.yandex.net"


SSH_OPTS = [
    "-o", "StrictHostKeyChecking=no",
    "-o", "CheckHostIP=no",
    "-o", "NoHostAuthenticationForLocalhost=yes",
    "-o", "BatchMode=yes",
    "-o", "LogLevel=ERROR",
    "-o", "UserKnownHostsFile=/dev/null",
    "-o", "ConnectTimeout=10"
]

SSH_DO_OPTS = SSH_OPTS + [
    "-o", "User=root",
    "-o", "IdentityFile=ructf2017_do_deploy"
]

SSH_YA_OPTS = SSH_OPTS + [
    "-o", "User=cloud",
    "-o", "IdentityFile=ructf2017_ya_deploy"
]


def gen_cloud_ip():
    cloud_ip = random.choice(CLOUD_HOSTS)
    return cloud_ip


def get_cloud_ip(team, may_generate=False):
    try:
        return open("db/team%d/cloud_ip" % team).read().strip()
    except FileNotFoundError as e:
        if may_generate:
            cloud_ip = gen_cloud_ip()
            print("Generating cloud_ip, assigned " + cloud_ip, file=sys.stderr)
            open("db/team%d/cloud_ip" % team, "w").write(cloud_ip)
            return cloud_ip
        else:
            return None


def log_progress(*params):
    print("progress:", *params, flush=True)


def call_unitl_zero_exit(params, redirect_out_to_err=True, attempts=60, timeout=10):
    if redirect_out_to_err:
        stdout = sys.stderr
    else:
        stdout = sys.stdout

    for i in range(attempts-1):
        if subprocess.call(params, stdout=stdout) == 0:
            return True
        time.sleep(timeout)
    if subprocess.call(params, stdout=stdout) == 0:
        return True

    return None
