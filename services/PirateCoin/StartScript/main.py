from geth_api.commands import GethController
from json import dump
from time import sleep
import subprocess
from random import randint
import os.path
import signal

signal.alarm(25 * 60)


def get_local_ip():
    try:
        ip = open("/home/PirateCoin/ip.txt").read().strip()
    except FileNotFoundError:
        ip_cmd = 'ifconfig eth0 | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1'
        for i in range(5):
          f = os.popen(ip_cmd)
          ip = f.read()
          if ip != "":
              return ip.strip()
          sleep(4)
        return randint(0, 1000000000)
    else:
        return ip


PATH_TO_GETH_IPC = "/root/node/geth.ipc"
PATH_TO_GETH_DIR = "/root/node/"
PATH_TO_GENESIS_BLOCK = "/home/PirateCoin/genesis-block.json"
PATH_TO_GETH_LOGS = "/root/geth.log"
PATH_TO_ETHASH = "/root/.ethash/"

geth_run_command = "geth " \
                   "--datadir {}" \
                   " --networkid 31337" \
                   " --rpc --rpcaddr 0.0.0.0 --rpcport 8545 --rpcapi 'db,eth,net,web3,personal'"\
                   " --port 30303" \
                   " --netrestrict '10.60.0.0/14,10.80.0.0/14,10.10.0.0/16'"\
                   " --maxpeers 30"\
                   " --verbosity 5"\
                   " --bootnodes 'enode://f7c62f793afbb6cb9667f1b8c4e0f527422b4b95713a79e17d20e1c4a5a81ff48c6564501118a9531adf5e92f011604ff224f559484172f09daa6884a84a10d3@10.10.10.101:1337'" \
                   " --ethstats node_{}:ructfe_secret_key@10.10.10.102:38030 2>> {}"\
    .format(PATH_TO_GETH_DIR, get_local_ip(), PATH_TO_GETH_LOGS)


if not os.path.isdir(PATH_TO_GETH_DIR):
    p1 = subprocess.Popen("geth --datadir {} init {}"
                          .format(PATH_TO_GETH_DIR, PATH_TO_GENESIS_BLOCK),
                          shell=True, start_new_session=True)
    p1.wait()
print("Geth dir initialized started")


print("Cleaning old DAG files...")
if os.path.isdir(PATH_TO_ETHASH):
    listing_command = "ls -t {}".format(PATH_TO_ETHASH)
    f = os.popen(listing_command)
    files_listing = f.read().strip("\n").split("\n")
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
print("Miner started")

p2.wait()
