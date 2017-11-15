import subprocess
import sys
import time
import random

DOMAIN = "cloud.alexbers.com"

CLOUD_HOSTS = ["5.45.248.218"]

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

def get_cloud_ip(team):
    try:
        return open("db/team%d/cloud_ip" % team).read().strip()
    except FileNotFoundError as e:
        cloud_ip = gen_cloud_ip()
        print("Generating cloud_ip, assigned %s" % cloud_ip, file=sys.stderr)
        open("db/team%d/cloud_ip" % team, "w").write(cloud_ip)
        return cloud_ip

def log_progress(*params):
    print("progress:", *params, flush=True)

def call_unitl_zero_exit(params, attempts=60, timeout=10):
    for i in range(attempts):
        if subprocess.call(params, stdout=sys.stderr) == 0:
            return True
        time.sleep(timeout)
    return None
