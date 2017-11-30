import json
import socket
from urllib.request import Request, urlopen
from urllib.error import URLError
from user_agents import get_useragent
from answer_codes import CheckerAnswers
from web3 import IPCProvider, Web3
from web3.contract import ConciseContract
from datetime import datetime


def check_service_state(team_addr):
    return CheckerAnswers.OK()