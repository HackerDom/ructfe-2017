from base64 import b64encode, b64decode

from db.model import Model, TextField, IntField
from torrent_format.bencoder import parse_dictionary
from utils import generate_uid


class TorrentFile(Model):
    announce = TextField(256)
    length = IntField()
    type = TextField(256)
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
        self.length = meta_dict[b'info'].get(b'length')
        self.uid = generate_uid()
        self.upload_by = upload_by
        if self.length is None:
            length = 0
            for file in meta_dict[b'info'][b'files']:
                length += file[b'length']
            self.length = length
            self.type = 'directory'
        else:
            self.type = 'file'

    def get_data(self):
        return b64decode(self.content)

    def __str__(self):
        return "TorrentFileInfo({})".format(self.__dict__)


class PrivateTorrentFile(TorrentFile):
    announce = TextField(256)
    length = IntField()
    type = TextField(256)
    name = TextField(256)
    uid = TextField(32)
    upload_by = TextField(256)
    content = TextField(long=True)
