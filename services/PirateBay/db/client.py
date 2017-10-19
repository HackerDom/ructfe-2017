import pymysql

from config import CONNECTION_PARAMS


class Query:
    def __init__(self, **params):
        self.params = params
        self.template = None

    @property
    def query(self):
        return self.template.format(**self.params)


class InsertQuery(Query):
    def __init__(self, **params):
        super().__init__(**params)
        self.template = "INSERT INTO {tbl_name} ({field_names}) VALUES ({values});"


class GetAllQuery(Query):
    def __init__(self, **params):
        super().__init__(**params)
        self.template = "SELECT * FROM {tbl_name};"


class CreateTableIfNotExistsQuery(Query):
    def __init__(self, **params):
        super().__init__(**params)
        self.template = "CREATE TABLE IF NOT EXISTS {tbl_name}({fields});"


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
