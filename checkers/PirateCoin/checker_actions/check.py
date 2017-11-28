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


def check_service_state(team_addr):
    return CheckerAnswers.OK()