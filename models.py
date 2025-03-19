from flask_mysqldb import MySQLdb, MySQL
import MySQLdb.cursors
from extensions import mysql



# ✅ **Utility Functions**
def get_record(query, params=()):
    """ Fetch a single record """
    with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone()


def get_records(query, params=()):
    """ Fetch multiple records """
    with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_query(query, params=()):
    """ Execute an INSERT, UPDATE, or DELETE query """
    with mysql.connection.cursor() as cursor:
        cursor.execute(query, params)
        mysql.connection.commit()

