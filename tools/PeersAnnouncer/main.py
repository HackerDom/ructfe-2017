from flask import Flask, jsonify
from web3 import RPCProvider, Web3
from datetime import datetime


app = Flask(__name__)
GETH_RPC_PATH = "10.10.10.101"

static_boot_node = ["enode://f7c62f793afbb6cb9667f1b8c4e0f527422b4b95713a79e17d20e1c4a5a81ff48c6564501118a9531adf5e92f011604ff224f559484172f09daa6884a84a10d3@10.10.10.101:1337"]
last_update = datetime.now().timestamp()


@app.route("/bootnodes.json")
def get_bootnodes():
    global cached_boot_nodes
    if datetime.now().timestamp() > last_update + 60:
        cached_boot_nodes = retrieve_main_node_peers()
    return jsonify(static_boot_node + cached_boot_nodes)


def retrieve_main_node_peers():
    w3 = Web3(RPCProvider(host=GETH_RPC_PATH))
    peers_list = w3.admin.peers
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


cached_boot_nodes = retrieve_main_node_peers()

if __name__ == '__main__':
    app.run("0.0.0.0", 80)

