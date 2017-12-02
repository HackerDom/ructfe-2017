import socket
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
from config import BLACK_MARKET_ADDR
from answer_codes import CheckerAnswers


def check_service_state(team_addr):  # todo implement it

    req = BLACK_MARKET_ADDR + \
        "/checkTeam_C6EDEE7179BD4E2887A5887901F23060?vulnboxIp={}"\
        .format(team_addr)
    try:
        try:
            result = urlopen(req, timeout=7).read().decode()
        except socket.timeout:
            result = urlopen(req, timeout=7).read().decode()
    except (HTTPError, URLError, socket.timeout) as e:
        return CheckerAnswers.CHECKER_ERROR(
            "",
            "Couldn't await checker helper answer ({}) at ({})".format(e, req))

    try:
        if int(result) < 60:
            return CheckerAnswers.MUMBLE(
                "Couldn't use contract properly! ",
                "{}s ago".format(int(result)))
    except ValueError:
        return CheckerAnswers.CHECKER_ERROR("", "Bad checker helper answer")
    return CheckerAnswers.OK()
