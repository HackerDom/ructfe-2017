from hashlib import sha512
from base64 import b64encode
from random import choice
from string import hexdigits
import pickle
from time import time


def generate_uid():
    return str(time() * 1000000)[:-2]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def cached_method(func):
    memory = {}

    def mem_func(*args, **kwargs):
        args_string = pickle.dumps((args, sorted(kwargs.items())))
        if args_string not in memory:
            memory[hash] = func(*args, **kwargs)
        return memory[hash]
    return mem_func


def get_sha512(data: bytes):
    hasher = sha512()
    hasher.update(data)
    return hasher.digest()


def get_base_of_hash(data: str):
    return b64encode(get_sha512(data.encode())).decode()
