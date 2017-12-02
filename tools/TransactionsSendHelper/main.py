from flask import Flask, request
from web3 import HTTPProvider, Web3
from web3.contract import ConciseContract
from multiprocessing import Process
import binascii


app = Flask(__name__)
IPC_ADDR = "/root/geth_service/checker_node/geth.ipc"
ACCOUNT_PASSWORD = "rjvgjcnth"
ACCOUNT_COINBASE = "0x85a3e0ffe7630de3bd772e5be27acdc57c11e566"
CONTRACT_ABI = []
FREE_TRANSACTION_TEXT = "0x" + binascii.hexlify(
    b"Ethers for everybody, FREE, and no one will go away unsatisfied!")\
    .decode()


@app.route("/sendTransaction")
def transaction_handler():
    t_to = request.args.get("to")
    t_value = request.args.get("value")
    spawn_transaction_process(sent_transaction_to_wallet, (t_to, t_value))
    return "Transaction sent in txpool!"


@app.route("/sendContractTransaction")
def contract_transaction_handler():
    t_to = request.args.get("to")
    t_value = request.args.get("value")
    spawn_transaction_process(send_transaction_to_contract, (t_to, t_value))
    return "Transaction sent in txpool!"


def spawn_transaction_process(func: callable, args: tuple):
    p = Process(target=func, args=args)
    p.start()


def send_transaction_to_contract(t_to, to_value):
    w3 = Web3(
        HTTPProvider("http://127.0.0.1:8545", request_kwargs={'timeout': 300}))
    w3.personal.unlockAccount(ACCOUNT_COINBASE, ACCOUNT_PASSWORD)

    contract_instance = w3.eth.contract(
        CONTRACT_ABI,
        t_to,
        ContractFactoryClass=ConciseContract)

    transaction_id = contract_instance.addToBalance(
       transact={
           "from": ACCOUNT_COINBASE,
           "gas": 40728,
           "value": int(to_value)
       }
    )
    print("Finished {}".format(transaction_id))
    return transaction_id


def sent_transaction_to_wallet(t_to, to_value):
    w3 = Web3(
        HTTPProvider("http://127.0.0.1:8545", request_kwargs={'timeout': 300}))
    w3.personal.unlockAccount(ACCOUNT_COINBASE, ACCOUNT_PASSWORD)
    transaction_id = w3.eth.sendTransaction({
       "to": t_to,
       "from": ACCOUNT_COINBASE,
       "value": 1000000000000,
       "data": FREE_TRANSACTION_TEXT
    })
    print("Finished {}".format(transaction_id))
    return transaction_id


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)