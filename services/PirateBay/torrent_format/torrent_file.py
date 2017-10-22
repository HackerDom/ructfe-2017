from db.model import Model, TextField, IntField
from torrent_format.bencoder import parse_dictionary
from utils import generate_uid


class TorrentFileInfo(Model):
    announce = TextField(256)
    length = IntField()
    type = TextField(256)
    name = TextField(256)
    uid = TextField(32)

    def __init__(self, data=None):
        if data is None:
            return
        meta_dict, _ = parse_dictionary(data)
        self.announce = meta_dict[b'announce'].decode()
        self.name = meta_dict[b'info'][b'name'].decode()
        self.length = meta_dict[b'info'].get(b'length')
        self.uid = generate_uid()
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
