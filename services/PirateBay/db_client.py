import pymysql

from config import CONNECTION_PARAMS, TORRENT_FILES_TABLE_NAME
from torrent_file import TorrentFileInfo

INSERT_FILE_INFO_TEMPLATE = "INSERT INTO %s ({}) VALUES ({});" % TORRENT_FILES_TABLE_NAME
GET_FILE_INFOS_TEMPLATE = "SELECT * FROM %s;" % TORRENT_FILES_TABLE_NAME

CONNECTION = pymysql.connect(**CONNECTION_PARAMS)


def make_insert_query(torrent_file_info):
    torrent_file_dict = torrent_file_info.__dict__
    keys = sorted(torrent_file_dict.keys())
    columns = ', '.join('`{}`'.format(field) for field in keys)
    values = ', '.join("'{}'".format(torrent_file_dict[field]) for field in keys)
    return INSERT_FILE_INFO_TEMPLATE.format(columns, values)


def load_torrent_file(raw_file_bytes):
    torrent_file_info = TorrentFileInfo(raw_file_bytes)
    with CONNECTION.cursor() as cursor:
        cursor.execute(make_insert_query(torrent_file_info))
    CONNECTION.commit()


def get_torrent_files():
    with CONNECTION.cursor() as cursor:
        cursor.execute(GET_FILE_INFOS_TEMPLATE)
        return list(cursor.fetchall())
