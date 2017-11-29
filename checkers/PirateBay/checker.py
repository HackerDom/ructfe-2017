#!/usr/bin/env python3
import os
import re
import traceback
from sys import argv, stderr
import requests
import sys
from requests.exceptions import ConnectionError, HTTPError

from generators import generate_login, generate_password, generate_torrent_dict, generate_name, generate_headers

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
REGISTER_URL_TEMPLATE = "http://{hostname}/signup?password={password}&login={login}"
UPLOAD_URL_TEMPLATE = "http://{hostname}/upload_private"
AUTH_URL_TEMPLATE = "http://{hostname}/signin?login={login}&password={password}"
PRIVATE_STORAGE_URL_TEMPLATE = "http://{hostname}/private_storage"


def print_to_stderr(*args):
    print(*args, file=sys.stderr)


def auth(hostname, login, password):
    auth_url = AUTH_URL_TEMPLATE.format(
        hostname=hostname,
        login=login,
        password=password,
    )
    r = requests.get(
        auth_url,
        headers=generate_headers()
    )
    return dict(r.request._cookies)


def info():
    print("vulns: 1")
    exit(OK)


def check(hostname):
    exit(OK)


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR


def put(hostname, flag_id, flag, vuln):
    login = generate_login()
    password = generate_password()
    name = generate_name()
    exit_code = OK
    try:
        register_request = requests.get(REGISTER_URL_TEMPLATE.format(
            hostname=hostname,
            password=password,
            login=login,
        ), headers=generate_headers())
        cookies = auth(hostname, login, password)
        register_request.raise_for_status()
        with open("buffer", "wb") as file:
            file.write(generate_torrent_dict(name, flag, login))
        with open('buffer', 'rb') as file:
            files = {'upload_file': file}
            upload_request = requests.post(
                UPLOAD_URL_TEMPLATE.format(hostname=hostname),
                cookies=cookies,
                files=files,
                headers=generate_headers(),
            )
            upload_request.raise_for_status()
    except ConnectionError as error:
        print_to_stderr("Connection error: hostname: {}, error: {}".format(hostname, error))
        exit_code = DOWN
    except HTTPError as error:
        print_to_stderr("HTTP Error: hostname: {}, error: {}".format(hostname, error))
        exit_code = MUMBLE
    finally:
        if os.path.exists("buffer"):
            os.remove("buffer")
    if exit_code == OK:
        print("{},{},{}".format(login, password, name))
    exit(exit_code)


def get(hostname, flag_id, flag, _):
    login, password, name = flag_id.split(',')
    try:
        cookies = auth(hostname, login, password)
        content = requests.get(
            PRIVATE_STORAGE_URL_TEMPLATE.format(hostname=hostname),
            cookies=cookies,
            headers=generate_headers(),
        ).content.decode()
        flag_pattern = re.compile("<td>{}</td>.*?<td>(.*?)</td>".format(name), re.DOTALL)
        matching = flag_pattern.search(content)
        if matching is None:
            exit(CORRUPT)
        if len(matching.groups()) == 0:
            exit(CORRUPT)
        if matching.group(1) != flag:
            exit(CORRUPT)
    except (ConnectionError, ConnectionRefusedError) as error:
        print_to_stderr("Connection error: hostname: {}, error: {}".format(hostname, error))
        exit(DOWN)
    except (HTTPError, UnicodeDecodeError) as error:
        print_to_stderr("HTTP or decoding error: hostname: {}, error: {}".format(hostname, error))
        exit(MUMBLE)
    exit(OK)


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def main():
    try:
        COMMANDS.get(argv[1], not_found)(*argv[2:])
    except Exception:
        traceback.print_exc()
        exit(CHECKER_ERROR)

if __name__ == '__main__':
    main()
