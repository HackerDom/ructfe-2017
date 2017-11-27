# from db.client import DBClient
# from config import DATABASE_NAME

# db_client = DBClient()
#
# CREATE_DB_TEMPLATE = "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"
#
# with db_client.connection.cursor() as cursor:
#     cursor.execute(CREATE_DB_TEMPLATE.format(DATABASE_NAME))
#
# db_client.connection.commit()
# db_client.use()
