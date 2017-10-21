import pymysql

from config import CONNECTION_PARAMS


class InsertQuery:
    def __init__(self, tbl_name, field_names, values):
        self.query = "INSERT INTO {tbl_name} ({field_names}) VALUES ({values});".format(
            tbl_name=tbl_name,
            field_names=', '.join(field_names),
            values="'{}'".format("', '".join(values))
        )


class GetAllQuery:
    def __init__(self, tbl_name):
        self.query = "SELECT * FROM {tbl_name};".format(
            tbl_name=tbl_name,
        )


class CreateTableIfNotExistsQuery:
    def __init__(self, tbl_name, fields):
        self.query = "CREATE TABLE IF NOT EXISTS {tbl_name}({fields});".format(
            tbl_name=tbl_name,
            fields=', '.join(' '.join(field) for field in fields),
        )


class FilterQuery:
    def __init__(self, tbl_name, filter_fields):
        self.query = "SELECT * FROM {tbl_name} WHERE {filter_fields};".format(
            tbl_name=tbl_name,
            filter_fields=' AND '.join("{}='{}'".format(*filter_field) for filter_field in filter_fields.items())
        )


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBClient(metaclass=Singleton):
    def __init__(self):
        self.connection = pymysql.connect(**CONNECTION_PARAMS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
