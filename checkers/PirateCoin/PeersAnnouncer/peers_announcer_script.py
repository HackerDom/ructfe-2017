import json
from time import sleep

from web3 import RPCProvider, Web3
from requests.exceptions import ConnectionError


GETH_RPC_PATH = "10.10.10.101"
static_boot_node = [
    "enode://f7c62f793afbb6cb9667f1b8c4e0f527422b4b95713a79e17d20e1c4a5a81ff48c6564501118a9531adf5e92f011604ff224f559484172f09daa6884a84a10d3@10.10.10.101:1337"
]
BOOT_NODES_JSON_FILE = "/var/www/html/bootnodes.json"


def retrieve_main_node_peers():
    w3 = Web3(RPCProvider(host=GETH_RPC_PATH))
    try:
        peers_list = w3.admin.peers
    except ConnectionError:
        print("RPC down")
        return []
    boot_nodes = []
    for peer in peers_list:
        try:
            node_pubkey = peer["id"]
            node_remote_addr = peer["network"]["remoteAddress"].split(":")[0]
            boot_nodes.append(
                "enode://{pubkey}@{ip}:30303"
                .format(
                    pubkey=node_pubkey,
                    ip=node_remote_addr))
        except (IndexError, KeyError, ValueError) as e:
            print(str(e))
    return boot_nodes


while True:
    peers = retrieve_main_node_peers()
    if peers:
        try:
            with open(BOOT_NODES_JSON_FILE, mode="w") as file:
                json.dump(static_boot_node + peers, file)
        except OSError as e:
            print("Got error on writing new nodes!")
    sleep(60)

