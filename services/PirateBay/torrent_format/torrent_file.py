import os
import re
from base64 import b64encode, b64decode
from random import choice, randint
from time import time

from mimesis import Food

from db.model import Model, TextField, IntField
from torrent_format.bencoder import parse_dictionary, make_dictionary
from utils import generate_uid


class TorrentFile(Model):
    announce = TextField(256)
    length = IntField()
    comment = TextField(256)
    name = TextField(256)
    uid = TextField(32)
    upload_by = TextField(256)
    content = TextField(long=True)

    def __init__(self, data=None, upload_by=""):
        if data is None:
            return
        self.content = b64encode(data).decode()
        meta_dict, _ = parse_dictionary(data)
        self.announce = meta_dict[b'announce'].decode()
        self.name = meta_dict[b'info'][b'name'].decode()
        self.comment = meta_dict[b'comment'].decode()
        self.length = meta_dict[b'info'].get(b'length')
        self.uid = generate_uid()
        self.upload_by = upload_by
        if self.length is None:
            length = 0
            for file in meta_dict[b'info'][b'files']:
                length += file[b'length']
            self.length = length

    def get_data(self):
        return b64decode(self.content)

    def __str__(self):
        return "TorrentFileInfo({})".format(self.__dict__)


class PrivateTorrentFile(TorrentFile):
    announce = TextField(256)
    length = IntField()
    comment = TextField(256)
    name = TextField(256)
    uid = TextField(32)
    upload_by = TextField(256)
    content = TextField(long=True)

    def __str__(self):
        return "PrivateTorrentFileInfo({})".format(self.__dict__)

food = Food('en')
food_regex = re.compile(r'^[a-zA-Z\s]+$')


def rand_food():
    new_food = choice([food.drink(), food.fruit(), food.dish(), food.spices(), food.vegetable()]).replace("'", "\\'")
    if food_regex.match(new_food):
        return new_food
    else:
        return rand_food()


def generate_torrent_dict(comment):
    length = randint(512, 10240)
    return make_dictionary({
        b'announce': b'ructfe.org',
        b'creation date': int(time()),
        b'comment': comment.encode(),
        b'created by': b'Pirate bay',
        b'info': {
            b'piece length': length,
            b'length': length,
            b'pieces': os.urandom(20),
            b'name': rand_food().encode(),
        }
    })
