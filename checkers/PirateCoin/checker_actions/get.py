import json
import binascii

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
from socket import socket

from requests.exceptions import ConnectionError
from web3 import RPCProvider, Web3
from web3.contract import ConciseContract
from web3.exceptions import BadFunctionCallOutput

from utils import create_request_object
from answer_codes import CheckerAnswers
from config import \
    GETH_RPC_PATH, ACCOUNT_ID, ACCOUNT_PASSWORD,\
    BLACK_MARKET_ADDR, SERVICE_COINBASE


TRANSACTION_COOLDOWN = 60
FREE_TRANSACTION_TEXT = "0x" + binascii.hexlify(
    b"Ethers for everybody, FREE, and no one will go away unsatisfied!")\
    .decode()


def get_check_contract(team_addr, flag_id, flag):
    contract_addr = flag_id

    req = BLACK_MARKET_ADDR + "/checkFlag_C6EDEE7179BD4E2887A5887901F23060?{}"\
        .format(urlencode(
                    {
                        "flag": flag,
                        "contractAddr": contract_addr
                    }))

    try:
        try:
            response = urlopen(req, timeout=7).read().decode()
        except socket.timeout:
            response = urlopen(req, timeout=7).read().decode()
        if response == "stolen":
            return CheckerAnswers.CORRUPT(
                "Unsynchronized balances in contract!",
                "flag has been already given to another team!"
            )
    except (URLError, socket.timeout) as e:
        return CheckerAnswers.CHECKER_ERROR(
            "", "Black Market is down! req = {}, e = {}".format(req, e))
    except HTTPError as e:
        return CheckerAnswers.CHECKER_ERROR(
            "", "Can't connect to BM req = {}, e = {}".format(req, e))

    req = create_request_object(SERVICE_COINBASE.format(team_addr))
    try:
        try:
            team_coinbase = urlopen(req, timeout=7).read().decode()
        except socket.timeout:
            team_coinbase = urlopen(req, timeout=7).read().decode()

        int(team_coinbase, 16)
    except (URLError, socket.timeout) as e:
        return CheckerAnswers.DOWN(
            "Can't reach team web server",
            "(req = {}, err = {})".format(req.full_url, e))
    except ValueError:
        return CheckerAnswers.MUMBLE("Can't parse team coinbase!", "")

    try:
        with open("contract_abi.json") as abi:
            contract_abi = json.load(abi)
    except OSError as e:
        return CheckerAnswers.CHECKER_ERROR(
            "", "can't open contract abi! ({})".format(e)
        )

    try:
        w3 = Web3(RPCProvider(host=GETH_RPC_PATH))
        w3.personal.unlockAccount(w3.eth.coinbase, ACCOUNT_PASSWORD)
        w3.eth.sendTransaction({
            "to": team_coinbase,
            "from": ACCOUNT_ID,
            "value": 1000000000000,
            "data": FREE_TRANSACTION_TEXT
        })

        contract_instance = w3.eth.contract(
            contract_abi,
            contract_addr,
            ContractFactoryClass=ConciseContract)

        contract_total_ethers = w3.eth.getBalance(contract_addr)

        try:
            total_tokens = int(contract_instance.totalBankBalance())
            checker_tokens = int(contract_instance.getUserBalance(ACCOUNT_ID))
        except BadFunctionCallOutput as e:
            return CheckerAnswers.MUMBLE(
                "Couldn't call expected contract methods!",
                "error calling on bankBalance() or getUserBalance()")
        except ValueError as e:
            return CheckerAnswers.MUMBLE(
                "Unexpected methods answers!",
                "can't parse int on calling bankBalance() or getUserBalance()")
    except ConnectionError:
        return CheckerAnswers.CHECKER_ERROR("", "Can't connect to node rpc")

    if total_tokens > contract_total_ethers:
        return CheckerAnswers.CORRUPT(
            "Unsynchronized balances in contract!",
            "bank balance > contract balance")

    if checker_tokens > total_tokens or checker_tokens > contract_total_ethers:
        return CheckerAnswers.CORRUPT(
            "Unsynchronized balances in contract!",
            "checker balance < contract balance")

    return CheckerAnswers.OK()
