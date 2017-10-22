from random import choice
from string import hexdigits
import pickle


def generate_uid():
    return ''.join(choice(hexdigits) for _ in range(32))


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
