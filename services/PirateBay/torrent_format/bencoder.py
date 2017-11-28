INT_START = b'i'
INT_END = b'e'
STRING_DELIMITER = b':'
DICT_START = b'd'
LIST_START = b'l'
LICT_END = b'e'  # list and dict end


class ParseError(Exception):
    pass


def parse_integer(data: bytes, start_index=0):
    end_index = data.find(INT_END, start_index)
    return int(data[start_index + 1:end_index]), end_index + 1


def parse_string(data: bytes, start_index=0):
    delim_index = data.find(STRING_DELIMITER, start_index)
    string_length = int(data[start_index:delim_index])
    return data[delim_index + 1:delim_index + string_length + 1], delim_index + string_length + 1


def parse_list(data: bytes, start_index=0):
    result = []
    index = start_index + 1
    current_byte = data[index:index + 1]
    while (current_byte != LICT_END) and (index < len(data)):
        parse = get_parser(current_byte)
        new_element, index = parse(data, index)
        result.append(new_element)
        current_byte = data[index:index + 1]
    return result, index + 1


def parse_dictionary(data: bytes, start_index=0):
    try:
        result, index = parse_list(data, start_index)
        result_iterator = iter(result)
        return dict(zip(result_iterator, result_iterator)), index
    except Exception:
        raise ParseError


def get_parser(current_byte):
    if current_byte.isdigit():
        return parse_string
    else:
        return {
            INT_START: parse_integer,
            LIST_START: parse_list,
            DICT_START: parse_dictionary,
        }[current_byte]


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
