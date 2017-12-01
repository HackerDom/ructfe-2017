import sqlite3

from config import DATABASE_FULL_PATH
from utils import Singleton


class InsertQuery:
    def __init__(self, tbl_name, field_names, values):
        self.query = "INSERT INTO {tbl_name} ({field_names}) VALUES ({values});".format(
            tbl_name=tbl_name,
            field_names=', '.join(field_names),
            values=", ".join(value for value in values)
        )


class GetAllQuery:
    def __init__(self, tbl_name, field_names, lower_bound, count):
        self.query = "SELECT {field_names} FROM {tbl_name} LIMIT {lower_bound}, {count};".format(
            field_names=', '.join(field_names),
            tbl_name=tbl_name,
            lower_bound=lower_bound,
            count=count,
        )


class CreateTableIfNotExistsQuery:
    def __init__(self, tbl_name, fields):
        self.query = "CREATE TABLE IF NOT EXISTS {tbl_name}({fields});".format(
            tbl_name=tbl_name,
            fields=', '.join(' '.join(field) for field in fields),
        )


class FilterQuery:
    def __init__(self, tbl_name, field_names, filter_fields, lower_bound, count):
        self.query = "SELECT {field_names} FROM {tbl_name} WHERE {filter_fields} LIMIT {lower_bound}, {count};".format(
            field_names=', '.join(field_names),
            tbl_name=tbl_name,
            filter_fields=' AND '.join(filter_fields),
            lower_bound=lower_bound,
            count=count,
        )


class GetCountQuery:
    def __init__(self, tbl_name, filter_fields=""):
        if filter_fields:
            self.query = "SELECT COUNT(*) FROM {tbl_name} WHERE {filter_fields};".format(
                tbl_name=tbl_name,
                filter_fields=' AND '.join(filter_fields),
            )
        else:
            self.query = "SELECT COUNT(*) FROM {tbl_name};".format(
                tbl_name=tbl_name,
            )


class DBClient(metaclass=Singleton):
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_FULL_PATH, check_same_thread=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
