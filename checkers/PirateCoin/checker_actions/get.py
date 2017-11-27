import json
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError
from user_agents import get_useragent
from answer_codes import CheckerAnswers
from web3 import IPCProvider, Web3
from web3.contract import ConciseContract
from datetime import datetime


REQUEST_STRING = "http://{}/latest_wallet_smart_contract"
TIMEOUT = 7
GETH_IPC_PATH = "/Users/ximik/ether_test_net/node2/geth.ipc"
ACCOUNT_ID = ""  # todo generate it
ACCOUNT_PASSWORD = "qwerty"


def create_request_object(team_addr):
    return Request(team_addr, headers={
        'User-Agent': get_useragent(),
        'Content-type': 'application/json'
    })


def get_check_contract(team_addr, flag_id, flag):
    contract_addr, contract_creation_time = flag_id.split(":")

    # await first 60 seconds due to contract creation
    if int(contract_creation_time) + 60 >= int(datetime.now().timestamp()):
        return CheckerAnswers.OK()

    # mb check BM if flag was given to attacker?

    w3 = Web3(IPCProvider(GETH_IPC_PATH))
    contract_real_balance = w3.eth.checkBalance(contract_addr)

    # get contract state by checking public field/method

    return CheckerAnswers.OK()
