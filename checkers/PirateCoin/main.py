from geth_api.commands import GethController
from random import getrandbits
from json import dump
import socket
from time import sleep
import subprocess
from random import randint
import os.path


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.82.235.1", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception as e:
        return randint(0, 1000000000)
    return local_ip


PATH_TO_GETH_IPC = "/root/node/geth.ipc"
PATH_TO_GETH_DIR = "/root/node/"
PATH_TO_GENESIS_BLOCK = "/root/genesis-block.json"
PATH_TO_GETH_LOGS = "/root/geth.log"
JS_SCRIPTS_PATH = "/root/geth_scripts"

geth_run_command = "geth " \
                   "--datadir {}" \
                   " --networkid 31337" \
                   " --port 30303" \
                   " --netrestrict '10.60.0.0/14,10.80.0.0/14'" \
                   " --bootnodes 'enode://2a564b0cd7c823fa66212cff17f06b5de73325cd09fc59beacc5cf16a331b48b33fdb3e1cf96adff2057f9e2ba5a6ce06e80959a63c201add0cceb8d92a305e9@10.82.201.2:31337'" \
                   " --ethstats node_{}:ructfe_secret_key@10.82.201.2:38030 2>> {}"\
    .format(PATH_TO_GETH_DIR, get_local_ip(), PATH_TO_GETH_LOGS)

if not os.path.isdir(PATH_TO_GETH_DIR):
    p1 = subprocess.Popen("geth --datadir {} init {}"
                          .format(PATH_TO_GETH_DIR, PATH_TO_GENESIS_BLOCK),
                          shell=True, start_new_session=True)
    p1.wait()

if os.path.exists(PATH_TO_GETH_IPC):
    os.remove(PATH_TO_GETH_IPC)

p2 = subprocess.Popen(geth_run_command, shell=True, start_new_session=True)
# await for ipc file creation

while not os.path.exists(PATH_TO_GETH_IPC):
    sleep(1)

geth_wrapper = GethController(PATH_TO_GETH_IPC, JS_SCRIPTS_PATH)

if not geth_wrapper.get_accounts():
    password = hex(getrandbits(256))[2:]
    account = geth_wrapper.create_account(password)
    try:
        with open(PATH_TO_GETH_DIR + "account_info.json", "w") as file:
            dump({"account": account.strip("\""), "password": password}, file)
    except OSError as e:
        print("Couldn't write account info! ({})".format(e))

geth_wrapper.start_miner(1)
print("OK")
p2.wait()
