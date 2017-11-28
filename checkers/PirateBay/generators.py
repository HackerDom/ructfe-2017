import os
from time import time
from random import randint, choice
from string import ascii_letters, digits

from bencoder import make_dictionary


with open("food") as food_file:
    FOOD = food_file.read().split('\n')

with open("names") as names_file:
    NAMES = names_file.read().split('\n')

with open("user-agents") as user_agents_file:
    USER_AGENTS = user_agents_file.read().split('\n')


def generate_torrent_dict(name, comment, login):
    length = randint(512, 10240)
    return make_dictionary({
        b'announce': b'ructfe.org',
        b'creation date': int(time()),
        b'comment': comment.encode(),
        b'created by': login.encode(),
        b'info': {
            b'piece length': length,
            b'length': length,
            b'pieces': os.urandom(20),
            b'name': name.encode()
        }
    })


def generate_login():
    return choice(NAMES) + "_" + "".join(choice(digits) for _ in range(20))


def generate_password():
    return "".join(choice(ascii_letters + digits) for _ in range(50))


def generate_name():
    return choice(FOOD)


def generate_user_agent():
    return choice(USER_AGENTS)


def generate_headers():
    return {'User-Agent': generate_user_agent()}

