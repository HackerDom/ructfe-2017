#!/usr/bin/env python3

import sys
from urllib.error import URLError
import traceback
from random import randint
from checker_actions import put, get, check

from answer_codes import OK, MUMBLE, CORRUPT, DOWN, CHECKER_ERROR


def close(code, public="", private="", flag_id=""):
    """
    :param code: answer code
    :param public: anyone will see it
    :param private: only for admins
    :param flag_id: cache for put->get
    :return:
    """
    if flag_id:
        print(flag_id)
        exit(code)
    if public:
        print(public)
    if private:
        print(private, file=sys.stderr)
    exit(code)


def on_check(command_ip):
    check_result = check.check_service_state(command_ip)
    close(**check_result)


def on_put(command_ip, flag_id, flag, vuln=None):
    put_result = put.put_ether_on_team_smart_contract(
        command_ip, flag_id, flag)
    close(**put_result)


def on_get(command_ip, flag_id, flag, vuln=None):
    get_result = get.get_check_contract(command_ip, flag_id, flag)
    close(**get_result)


def on_info(*args):
    close(OK, "vulns: 1:1")


COMMANDS = {
    'check': on_check,
    'put': on_put,
    'get': on_get,
    'info': on_info
}


def not_found(*args):
    close(
        CHECKER_ERROR,
        "Checker error",
        "Unsupported command {}".format(sys.argv[1]))


if __name__ == '__main__':
    if randint(0, 9) == 9:
        close(OK, "rnd")
    try:
        COMMANDS.get(sys.argv[1].lower(), not_found)(*sys.argv[2:])
    except URLError as e:
        close(DOWN, "Bad command address", private="Checksystem fail {}"
              .format(traceback.format_exc()))
    except OSError as e:
        close(DOWN, "Socket I/O error", private="SOCKET ERROR: {}".format(
            traceback.format_exc()))
    except Exception as e:
        close(DOWN, "Unknown error", private="INTERNAL ERROR: {}"
              .format(traceback.format_exc()))