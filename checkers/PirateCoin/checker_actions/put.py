import os
import json
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError
from user_agents import get_useragent
from answer_codes import CheckerAnswers
from geth_api.commands import GethController


PATH_TO_GETH_IPC = "/root/node/geth.ipc"
PATH_TO_GETH_SCRIPTS = "/root/checker/scripts"
REQUEST_STRING = "http://{}/latest_wallet_smart_contract"
TIMEOUT = 7


def create_request_object(team_addr):
    return Request(team_addr, headers={
        'User-Agent': get_useragent(),
        'Content-type': 'application/json'
    })


def put_ether_on_team_smart_contract(team_addr, id, flag):
    if not os.path.exists(PATH_TO_GETH_IPC):
        return CheckerAnswers.CHECKER_ERROR("", "Couldn't find geth.ipc!")

    try:
        json_object = urlopen(
            create_request_object(REQUEST_STRING.format(team_addr)),
            timeout=TIMEOUT)\
            .read()\
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

    geth_controller = GethController(PATH_TO_GETH_IPC, PATH_TO_GETH_SCRIPTS)




