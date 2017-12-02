import json
import socket

from random import randint
from urllib.request import urlopen
from urllib.error import URLError
from urllib.parse import urlencode

from web3 import RPCProvider, Web3
from web3.contract import ConciseContract

from requests.exceptions import ConnectionError
from answer_codes import CheckerAnswers
from utils import create_request_object
from config import \
    GETH_RPC_PATH, ACCOUNT_PASSWORD, \
    SERVICE_FIRST_CONTRACT_ADDR_URL, BLACK_MARKET_ADDR


def put_ether_on_team_smart_contract(team_addr, id, flag):
    wei_per_transaction = 10 ** 17
    # (1-20 ethers)

    gas_per_transaction = 40728

    try:
        with open("contract_abi.json") as abi:
            contract_abi = json.load(abi)
    except OSError as e:
        return CheckerAnswers.CHECKER_ERROR("", "can't open contract abi!")

    req = create_request_object(
                SERVICE_FIRST_CONTRACT_ADDR_URL.format(team_addr))
    try:
        try:
            contract_addr = urlopen(req, timeout=7).read().decode()
        except socket.timeout:
            contract_addr = urlopen(req, timeout=7).read().decode()
        if contract_addr == "":
            return CheckerAnswers.MUMBLE(
                "Couldn't get team contract",
                "Team hasn't generated block contract!"
            )
    except KeyError as e:
        return CheckerAnswers.MUMBLE(
            "Incorrect json-api schema response req",
            "req = {}, e = {}".format(req.full_url, e))
    except socket.timeout as e:
        return CheckerAnswers.MUMBLE(
            "Service response timed out!",
            "req = {}, e = {}".format(req.full_url, e))
    except URLError as e:
        return CheckerAnswers.DOWN(
            "Can't reach service address!",
            "req = {}, e = {}".format(req.full_url, e))

    req = BLACK_MARKET_ADDR + "/putFlag_C6EDEE7179BD4E2887A5887901F23060?{}"\
        .format(
                urlencode(
                    {
                        "flag": flag,
                        "contractAddr": contract_addr,
                        "sum": int(wei_per_transaction),
                        "vulnboxIp": team_addr
                    }))

    try:
        try:
            urlopen(req, timeout=7).read().decode()
        except socket.timeout:
            urlopen(req, timeout=7).read().decode()
    except (URLError, socket.timeout) as e:
        return CheckerAnswers.CHECKER_ERROR(
           "", "Black Market is down! ({}), req = {}".format(e, req))

    try:
        w3 = Web3(RPCProvider(host=GETH_RPC_PATH))
        contract_instance = w3.eth.contract(
            contract_abi,
            contract_addr,
            ContractFactoryClass=ConciseContract
        )

        transaction_id = contract_instance.addToBalance(
           transact={
               "from": w3.eth.coinbase,
               "gas": gas_per_transaction,
               "value": wei_per_transaction
           }
        )

    except ConnectionError as e:
        return CheckerAnswers.CHECKER_ERROR(
            "", "can't connect to checker rpc! {}".format(e))

    # flag_id = contract_addr
    return CheckerAnswers.OK(flag_id="{}".format(contract_addr))
