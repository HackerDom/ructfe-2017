import json
import socket

from datetime import datetime
from random import randint
from urllib.request import Request, urlopen
from urllib.error import URLError

from web3 import IPCProvider, Web3
from web3.contract import ConciseContract

from user_agents import get_useragent
from answer_codes import CheckerAnswers
from config import \
    GETH_IPC_PATH, ACCOUNT_PASSWORD, SERVICE_FIRST_CONTRACT_ADDR_URL


TIMEOUT = 7


def create_request_object(team_addr):
    return Request(team_addr, headers={
        'User-Agent': get_useragent(),
        #'Content-type': 'application/json'
    })


def put_ether_on_team_smart_contract(team_addr, id, flag):
    wei_per_transaction = 10 ** 18 * randint(1, 20)  # (1-20 ethers)
    gas_per_transaction = 400000

    try:
        with open("contract_abi.json") as abi:
            contract_abi = json.load(abi)
    except OSError as e:
        return CheckerAnswers.CHECKER_ERROR("", str(e))

    try:
        contract_addr = urlopen(
            create_request_object(
                SERVICE_FIRST_CONTRACT_ADDR_URL.format(team_addr)),
            timeout=TIMEOUT) \
            .read() \
            .decode()
        contract_addr = contract_addr
    except KeyError as e:
        return CheckerAnswers.MUMBLE(
            "Incorrect json-api schema response", str(e)
        )
    except socket.timeout:
        return CheckerAnswers.MUMBLE(
            "Service response timed out!", ""
        )
    except URLError as e:
        return CheckerAnswers.DOWN(
            "Can't reach service address!", str(e)
        )

    w3 = Web3(IPCProvider(GETH_IPC_PATH))
    w3.personal.unlockAccount(w3.eth.coinbase, ACCOUNT_PASSWORD)

    contract_instance = w3.eth.contract(
        contract_abi,
        contract_addr,
        ContractFactoryClass=ConciseContract
    )

    transaction_id = contract_instance.addToBalance(
        transact={
            "from": w3.eth.coinbase,
            "gas": gas_per_transaction,
            "value": wei_per_transaction}
    )

    # todo put flag in the black market: contract_addr => flag

    # flag_id = contract:wei:transaction_timestamp
    return CheckerAnswers.OK(flag_id="{}:{}:{}".format(
        contract_addr, wei_per_transaction, int(datetime.now().timestamp())))
