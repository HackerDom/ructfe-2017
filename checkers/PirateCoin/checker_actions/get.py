import json

from datetime import datetime
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError
from socket import socket

from web3 import IPCProvider, Web3
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput

from answer_codes import CheckerAnswers
from config import \
    GETH_IPC_PATH, ACCOUNT_ID, ACCOUNT_PASSWORD, BLACK_MARKET_ADDR


TIMEOUT = 8
TRANSACTION_COOLDOWN = 60


def get_check_contract(team_addr, flag_id, flag):
    contract_addr, wei_in_transaction, contract_creation_time \
        = flag_id.split(":")

    try:
        response = urlopen(BLACK_MARKET_ADDR + "/checkFlag?{}".format(
            urlencode(
                {
                    "flag": flag,
                    "contractAddr": contract_addr
                })), timeout=TIMEOUT).read().decode()
        if response == "stolen":
            return CheckerAnswers.CORRUPT(
                "Unsynchronized balances in contract!",
                "flag has been already given to another team!"
            )
    except (URLError, socket.timeout):
        return CheckerAnswers.CHECKER_ERROR("", "Black Market is down!")

    if int(contract_creation_time) + TRANSACTION_COOLDOWN >= \
            int(datetime.now().timestamp()):
        return CheckerAnswers.OK()

    try:
        with open("contract_abi.json") as abi:
            contract_abi = json.load(abi)
    except OSError as e:
        return CheckerAnswers.CHECKER_ERROR("", str(e))

    w3 = Web3(IPCProvider(GETH_IPC_PATH))
    w3.personal.unlockAccount(w3.eth.coinbase, ACCOUNT_PASSWORD)

    contract_instance = w3.eth.contract(
        contract_abi,
        contract_addr,
        ContractFactoryClass=ConciseContract)

    w3 = Web3(IPCProvider(GETH_IPC_PATH))
    contract_ethereum_balance = w3.eth.getBalance(contract_addr)
    try:
        bank_balance = int(contract_instance.totalBankBalance())
        own_balance = int(contract_instance.getUserBalance(ACCOUNT_ID))
    except BadFunctionCallOutput:
        return CheckerAnswers.MUMBLE(
            "Couldn't call expected contract methods!",
            "error calling on bankBalance() or getUserBalance()")
    except ValueError:
        return CheckerAnswers.MUMBLE(
            "Unexpected methods answers!",
            "can't parse int on calling bankBalance() or getUserBalance()")

    if bank_balance > contract_ethereum_balance:
        return CheckerAnswers.CORRUPT(
            "Unsynchronized balances in contract!",
            "bank balance > contract balance")

    if own_balance < bank_balance or own_balance < contract_ethereum_balance:
        return CheckerAnswers.CORRUPT(
            "Unsynchronized balances in contract!",
            "checker balance < contract balance")

    if own_balance != int(wei_in_transaction):
        return CheckerAnswers.CORRUPT(
            "Unexpected amount of tokens on wallet!",
            "wallet != sent_wei")

    return CheckerAnswers.OK()
