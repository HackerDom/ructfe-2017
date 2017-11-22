import pymysql

from config import CONNECTION_PARAMS, DATABASE_NAME
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


class IncCountQuery:
    def __init__(self, tbl_name, model_name):
        self.query = "UPDATE {tbl_name} SET cnt = cnt + 1 WHERE name = '{model_name}';".format(
            tbl_name=tbl_name,
            model_name=model_name,
        )


class CreateIfCounterNotExists:
    def __init__(self, tbl_name, model_name):
        self.query = "INSERT INTO {tbl_name} (`NAME`, `CNT`) SELECT * FROM (SELECT '{model_name}', 0) AS TMP WHERE NOT EXISTS ( SELECT NAME FROM {tbl_name} WHERE NAME={model_name}) LIMIT 1;".format(
            tbl_name=tbl_name,
            model_name=model_name,
        )


class GetCountQuery:
    def __init__(self, tbl_name, model_name):
        self.query = "SELECT CNT FROM {tbl_name} WHERE NAME='{model_name}';".format(
            tbl_name=tbl_name,
            model_name=model_name,
        )


class DBClient(metaclass=Singleton):
    def use(self, db_name=DATABASE_NAME):
        self.connection.close()
        CONNECTION_PARAMS['db'] = db_name
        self.connection = pymysql.connect(**CONNECTION_PARAMS)

    def __init__(self):
        self.connection = pymysql.connect(**CONNECTION_PARAMS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
