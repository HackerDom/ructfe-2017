from base64 import b64encode, b64decode

from db.model import Model, TextField, IntField
from torrent_format.bencoder import parse_dictionary, ParseError
from utils import generate_uid


class InvalidTorrentFileError(Exception):
    pass


class TorrentFile(Model):
    announce = TextField(40)
    length = IntField()
    comment = TextField(100)
    name = TextField(100)
    uid = TextField(32)
    upload_by = TextField(50)
    content = TextField(long=True)

    def __init__(self, data=None, upload_by=""):
        try:
            if data is None:
                return
            self.content = b64encode(data).decode()
            meta_dict, _ = parse_dictionary(data)
            self.announce = meta_dict[b'announce'].decode()
            self.name = meta_dict[b'info'][b'name'].decode()
            self.comment = meta_dict.get(b'comment', b'').decode()
            self.length = meta_dict[b'info'].get(b'length')
            self.uid = generate_uid()
            self.upload_by = upload_by
            if self.length is None:
                length = 0
                for file in meta_dict[b'info'][b'files']:
                    length += file[b'length']
                self.length = length
        except (ParseError, KeyError):
            raise InvalidTorrentFileError("Incorrect fields")

    def get_data(self):
        return b64decode(self.content)

    def __str__(self):
        return "TorrentFileInfo({})".format(self.__dict__)


class PrivateTorrentFile(TorrentFile):
    announce = TextField(40)
    length = IntField()
    comment = TextField(100)
    name = TextField(100)
    uid = TextField(32)
    upload_by = TextField(50)
    content = TextField(long=True)

    def __str__(self):
        return "PrivateTorrentFileInfo({})".format(self.__dict__)
