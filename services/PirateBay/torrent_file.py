INT_START = b'i'
INT_END = b'e'
STRING_DELIMITER = b':'
DICT_START = b'd'
LIST_START = b'l'
LICT_END = b'e'  # list and dict end


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
    result, index = parse_list(data, start_index)
    result_iterator = iter(result)
    return dict(zip(result_iterator, result_iterator)), index


def get_parser(current_byte):
    if current_byte.isdigit():
        return parse_string
    else:
        return {
            INT_START: parse_integer,
            LIST_START: parse_list,
            DICT_START: parse_dictionary,
        }[current_byte]


def parse_torrent_file(data: bytes):
    return parse_dictionary(data)[0]


class TorrentFileInfo:
    def __init__(self, data):
        meta_dict = parse_torrent_file(data)
        self.announce = meta_dict[b'announce'].decode()
        self.name = meta_dict[b'info'][b'name'].decode()
        self.length = meta_dict[b'info'].get(b'length')
        if self.length is None:
            length = 0
            for file in meta_dict[b'info'][b'files']:
                length += file[b'length']
            self.length = length
            self.type = 'directory'
        else:
            self.type = 'file'

    def __str__(self):
        return "TorrentFileInfo({})".format(self.__dict__)
