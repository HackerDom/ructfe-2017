from geth_api.commands import GethController
from json import dump, loads
from time import sleep
import subprocess
from random import randint
from urllib.request import urlopen
import os.path
import signal


def get_local_ip():
    try:
        with open(TEAM_IP_FILE) as ip_file:
            return ip_file.read().strip()
    except OSError:
        return randint(0, 1000000000)


def add_nodes():
    try:
        nodes = loads(urlopen(DYNAMIC_BOOTNODES, timeout=15).read().decode())
        for node in nodes:
            geth_wrapper.add_peer(node)
    except Exception as e:
        with open("start_err.log", mode="w") as file_err:
            file_err.write(str(e))


TEAM_IP_FILE = "/home/PirateCoin/ip.txt"
STATIC_BOOTNODES = [
    "enode://f7c62f793afbb6cb9667f1b8c4e0f527422b4b95713a79e17d20e1c4a5a81ff48c6564501118a9531adf5e92f011604ff224f559484172f09daa6884a84a10d3@10.10.10.101:1337"
]
DYNAMIC_BOOTNODES = "http://10.10.10.101/bootnodes.json"
PATH_TO_GETH_IPC = "/home/PirateCoin/node/geth.ipc"
PATH_TO_GETH_DIR = "/home/PirateCoin/node/"
PATH_TO_GENESIS_BLOCK = "/home/PirateCoin/genesis-block.json"
PATH_TO_GETH_LOGS = "/home/PirateCoin/geth.log"
PATH_TO_ETHASH = "/home/PirateCoin/.ethash/"



try:
    dyn_nodes = loads(urlopen(DYNAMIC_BOOTNODES, timeout=15).read().decode())
    STATIC_BOOTNODES = list(set(STATIC_BOOTNODES + dyn_nodes))
except Exception:
    pass

geth_run_command = "geth" \
                   " --datadir {geth_path}" \
                   " --networkid 1337" \
                   " --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi 'db,eth,net,web3,admin,personal'"\
                   " --port 30303" \
                   " --netrestrict '10.60.0.0/14,10.80.0.0/14,10.10.0.0/16'"\
                   " --maxpeers 30"\
                   " --verbosity 5"\
                   " --ethash.dagdir {dagdir}"\
                   " --bootnodes '{bootnodes}'" \
                   " --ethstats node_{local_ip}:ructfe_secret_key@10.10.10.102:38030 2>> {get_logs}"\
    .format(
        geth_path=PATH_TO_GETH_DIR,
        bootnodes=",".join(STATIC_BOOTNODES),
        local_ip=get_local_ip(),
        get_logs=PATH_TO_GETH_LOGS,
        dagdir=PATH_TO_ETHASH
)


if not os.path.isdir(PATH_TO_GETH_DIR):
    p1 = subprocess.Popen("geth --datadir {} init {}"
                          .format(PATH_TO_GETH_DIR, PATH_TO_GENESIS_BLOCK),
                          shell=True, start_new_session=True)
    p1.wait()
print("Geth dir initialized started")


print("Cleaning old DAG files...")
if os.path.isdir(PATH_TO_ETHASH):
    listing_command = "ls -t {}".format(PATH_TO_ETHASH)
    fl = os.popen(listing_command)
    files_listing = fl.read().strip("\n").split("\n")
    for file in files_listing[2:]:
        os.remove(PATH_TO_ETHASH + file)


if os.path.exists(PATH_TO_GETH_IPC):
    os.remove(PATH_TO_GETH_IPC)
print("Cleaning old ipc file started")


p2 = subprocess.Popen(geth_run_command, shell=True, start_new_session=True)
while not os.path.exists(PATH_TO_GETH_IPC):
    sleep(1)
print("geth.ipc found!")


geth_wrapper = GethController(PATH_TO_GETH_IPC)
if not geth_wrapper.get_accounts():
    password = "qwer"
    account = geth_wrapper.create_account(password)
    try:
        with open(PATH_TO_GETH_DIR + "account_info.json", "w") as file:
            dump({"account": account.strip("\""), "password": password}, file)
    except OSError as e:
        print("Couldn't write account info! ({})".format(e))
print("Account created")


geth_wrapper.start_miner(1)
print("Miner started in single thread!")

for i in range(10):
    add_nodes()
    sleep(60)

while True:
    if p2.poll() is not None:  # oops, geth is dead?
        signal.alarm(1)
        sleep(1)
    add_nodes()
    if geth_wrapper.get_current_miner_hashrate() / 1024 < 5:
        signal.alarm(1)  # restart container on low hash rate
        sleep(1)
    sleep(60)
