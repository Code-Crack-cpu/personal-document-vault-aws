from contextlib import contextmanager

import mysql.connector
from flask import current_app


@contextmanager
def get_connection():
    connection = mysql.connector.connect(**current_app.config["MYSQL_CONFIG"])
    try:
        yield connection
    finally:
        connection.close()


def fetch_one(query, params=()):
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            cursor.close()


def fetch_all(query, params=()):
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()


def execute(query, params=()):
    with get_connection() as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error:
            connection.rollback()
            raise
        finally:
            cursor.close()
