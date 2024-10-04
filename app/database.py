import datetime
import json
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()


async def db_start():
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "id INTEGER PRIMARY KEY,"
                   "date_added TEXT,"
                   "name TEXT)"
                   )

    cursor.execute("CREATE TABLE IF NOT EXISTS bundles("
                   "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "created_date TEXT,"
                   "author_id INTEGER,"
                   "name TEXT,"
                   "price INTEGER,"
                   "company TEXT,"
                   "date_interview TEXT,"
                   "direction TEXT,"
                   "assembling JSON"
                   ")"
                   )
    connection.commit()


def add_user(user_id: int, name: str):
    time = str(datetime.datetime.now())
    cursor.execute('INSERT OR REPLACE INTO users (id, date_added, name) VALUES (?, ?, ?)',
                   (user_id, time, name))
    connection.commit()


def add_bundle(*, author_id: int, name: str, price: int, company: str, date_interview: str, direction: str,
               assembly: list):
    created_date = str(datetime.datetime.now())
    cursor.execute(
        'INSERT OR REPLACE INTO bundles (created_date, author_id, name, price, company, date_interview, direction, assembling) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (created_date, author_id, name, price, company, date_interview, direction, json.dumps(assembly, default=obj_dict)))
    connection.commit()

def obj_dict(obj):
    return obj.__dict__