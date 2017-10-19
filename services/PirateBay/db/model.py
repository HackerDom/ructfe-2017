import pickle

from db.client import GetAllQuery, InsertQuery, CreateTableIfNotExistsQuery, DBClient
from config import TORRENT_FILES_TABLE_NAME

db_client = DBClient()


def cached_method(func):
    memory = {}

    def mem_func(*args, **kwargs):
        args_string = pickle.dumps((args, sorted(kwargs.items())))
        if args_string not in memory:
            memory[hash] = func(*args, **kwargs)
        return memory[hash]
    return mem_func


class ValidationError(Exception):
    pass


class TextField:
    def __init__(self, max_length):
        self.max_length = max_length

    @property
    def mysql_format(self):
        return "VARCHAR({}) NOT NULL".format(self.max_length)


class IntField:
    @property
    def mysql_format(self):
        return "INT NOT NULL"


class Model:
    @classmethod
    @cached_method
    def get_fields(cls):
        return dict(field for field in cls.__dict__.items()
                    if (not field[0].startswith("__")) and
                    (not field[0].endswith("__")) and
                    not callable(getattr(cls, field[0])))

    @classmethod
    def validate(cls, fields):
        for field_name, _ in cls.get_fields().items():
            if field_name not in fields:
                raise ValidationError("Field {} is required".format(field_name))

    @classmethod
    def table_name(cls):
        return TORRENT_FILES_TABLE_NAME + "_" + cls.__name__

    @classmethod
    def create_table_if_not_exists(cls):
        table_name = cls.table_name()
        fields = ", ".join(
            field_name + " " + field_type.mysql_format for field_name, field_type in cls.get_fields().items()
        )
        create_table_if_not_exists_query = CreateTableIfNotExistsQuery(
            tbl_name=table_name,
            fields=fields,
        ).query
        with db_client.connection.cursor() as cursor:
            cursor.execute(create_table_if_not_exists_query)
        db_client.connection.commit()

    @classmethod
    def create(cls, **fields):
        cls.validate(fields)
        cls.create_table_if_not_exists()
        table_name = cls.table_name()
        model_fields = cls.get_fields()
        sorted_field_names = sorted(model_fields.keys())
        field_values = [str(fields[field_name]) for field_name in sorted_field_names]
        field_names_param = ", ".join(sorted_field_names)
        field_values_param = "'{}'".format("', '".join(field_values))
        insert_query = InsertQuery(
            tbl_name=table_name,
            field_names=field_names_param,
            values=field_values_param,
        ).query
        with db_client.connection.cursor() as cursor:
            cursor.execute(insert_query)
        db_client.connection.commit()

    def save(self):
        type(self).create(**self.__dict__)

    @classmethod
    def all(cls):
        get_all_query = GetAllQuery(tbl_name=cls.table_name()).query
        with db_client.connection.cursor() as cursor:
            cursor.execute(get_all_query)
            return list(cursor.fetchall())
