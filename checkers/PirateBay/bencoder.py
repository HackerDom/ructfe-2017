INT_START = b'i'
INT_END = b'e'
STRING_DELIMITER = b':'
DICT_START = b'd'
LIST_START = b'l'
LICT_END = b'e'  # list and dict end


def make_integer(num: int):
    return INT_START + str(num).encode() + INT_END


def make_string(source: bytes):
    return str(len(source)).encode() + STRING_DELIMITER + source


def make_list(obj_list: list):
    return LIST_START + b''.join(MAKERS[type(obj)](obj) for obj in obj_list) + LICT_END


def make_dictionary(obj_dict: dict):
    sorted_keys = sorted(obj_dict.keys())
    return DICT_START + b''.join(make_string(key) + MAKERS[type(obj_dict[key])](obj_dict[key])
                                 for key in sorted_keys) + LICT_END


MAKERS = {
    list: make_list,
    int: make_integer,
    bytes: make_string,
    dict: make_dictionary,
}
