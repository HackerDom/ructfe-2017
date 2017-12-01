import socket
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from utils import create_request_object
from config import BLACK_MARKET_ADDR
from answer_codes import CheckerAnswers


def check_service_state(team_addr):  # todo implement it
    req_object = create_request_object(
        BLACK_MARKET_ADDR +
        "/checkTeam_C6EDEE7179BD4E2887A5887901F23060?vulnboxIp={}"
        .format(team_addr))
    try:
        result = urlopen(req_object, timeout=15)
    except (HTTPError, URLError, socket.timeout):
        return CheckerAnswers.CHECKER_ERROR("", "Couldn't await checker helper answer")

    try:
        if int(result) < 60:
            return CheckerAnswers.MUMBLE(
                "Couldn't use contract properly! ",
                "{} ago".format(int(result)))
        return CheckerAnswers.OK()
    except ValueError:
        return CheckerAnswers.CHECKER_ERROR("", "Bad checker helper answer")
