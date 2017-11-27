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


def put_ether_on_team_smart_contract(team_addr, id, flag):
    wei_per_transaction = 10 ** 18  # (1 ether)
    gas_per_transaction = 400000

    try:
        with open("contract_abi.json") as abi:
            contract_abi = json.load(abi)
    except OSError as e:
        return CheckerAnswers.CHECKER_ERROR("", str(e))

    try:
        json_object = urlopen(
            create_request_object(REQUEST_STRING.format(team_addr)),
            timeout=TIMEOUT) \
            .read() \
            .decode()

        contract_addr = json.loads(json_object)["contract"]
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

    transaction_id = contract_instance.sendMoney(
        transact={
            "from": w3.eth.coinbase,
            "gas": gas_per_transaction,
            "value": wei_per_transaction}
    )

    # todo put flag in the black market: contract_addr => flag

    return CheckerAnswers.OK(flag_id="{}:{}".format(
        contract_addr, int(datetime.now().timestamp())))
