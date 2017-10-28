from config import TORRENT_FILES_TABLE_NAME
from db.client import GetAllQuery, InsertQuery, CreateTableIfNotExistsQuery, DBClient, FilterQuery
from utils import cached_method

db_client = DBClient()


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
    def make_from_field_values(cls, field_values):
        field_names = sorted(cls.get_fields().keys())
        model_object = cls()
        for field_name, field_value in zip(field_names, field_values):
            setattr(model_object, field_name, field_value)
        return model_object

    @classmethod
    @cached_method
    def get_fields(cls):
        fields = (field for field in cls.__dict__.items() if (not field[0].startswith("__")) and
                  (not field[0].endswith("__")) and not callable(getattr(cls, field[0])))
        return dict(fields)

    @classmethod
    @cached_method
    def get_field_names(cls):
        return sorted(cls.get_fields().keys())

    @classmethod
    def validate(cls, fields, check_required=True):
        real_fields = [field.split('__')[0] for field in fields]
        for field_name in real_fields:
            if field_name not in cls.get_fields():
                raise ValidationError("Undeclared field: {}".format(field_name))
        if not check_required:
            return
        for field_name, _ in cls.get_fields().items():
            if field_name not in real_fields:
                raise ValidationError("Field {} is required".format(field_name))

    @classmethod
    def table_name(cls):
        return TORRENT_FILES_TABLE_NAME + "_" + cls.__name__

    @classmethod
    def create_table_if_not_exists(cls):
        table_name = cls.table_name()
        fields = [(field_name, field_type.mysql_format) for field_name, field_type in cls.get_fields().items()]
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
        field_values = ["'{}'".format(fields[field_name]) for field_name in sorted_field_names]
        field_names_param = sorted_field_names
        field_values_param = field_values
        insert_query = InsertQuery(
            tbl_name=table_name,
            field_names=field_names_param,
            values=field_values_param,
        ).query
        # print(insert_query)
        with db_client.connection.cursor() as cursor:
            cursor.execute(insert_query)
        db_client.connection.commit()

    def save(self):
        type(self).create(**self.__dict__)

    @classmethod
    def all(cls):
        cls.create_table_if_not_exists()
        get_all_query = GetAllQuery(tbl_name=cls.table_name(), field_names=cls.get_field_names()).query
        with db_client.connection.cursor() as cursor:
            cursor.execute(get_all_query)
            object_tuples = cursor.fetchall()
            return [cls.make_from_field_values(object_tuple) for object_tuple in object_tuples]

    @staticmethod
    def format_field_filter(field_name, field_value):
        field, *params = field_name.split('__')
        if not params:
            return "{}='{}'".format(field_name, field_value)
        else:
            if params[0] == 'contains':
                return "{} LIKE '%{}%'".format(field, field_value)
            else:
                raise ValueError("Unexpected options: {}".format(",".join(params)))

    @classmethod
    def filter(cls, **fields):
        cls.validate(fields, check_required=False)
        cls.create_table_if_not_exists()
        filter_fields = [cls.format_field_filter(*field) for field in fields.items()]
        filter_query = FilterQuery(
            tbl_name=cls.table_name(),
            field_names=sorted(cls.get_fields().keys()),
            filter_fields=filter_fields
        ).query
        with db_client.connection.cursor() as cursor:
            cursor.execute(filter_query)
            object_tuples = cursor.fetchall()
            return [cls.make_from_field_values(object_tuple) for object_tuple in object_tuples]
