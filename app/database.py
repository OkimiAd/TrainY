import datetime
import json
import sqlite3
from email.policy import default

connection = sqlite3.connect('database.db')
cursor = connection.cursor()


async def db_start():
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "id INTEGER PRIMARY KEY,"
                   "date_added TEXT,"
                   "name TEXT,"
                   "available_bundles JSON DEFAULT('[]'))"
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
        (created_date, author_id, name, price, company, date_interview, direction,
         json.dumps(assembly, default=obj_dict)))
    connection.commit()


def add_bundle_for_user(*, user_id: int, bundle_id: int):
    original_list: tuple = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()
    y: list = json.loads(original_list[0])
    y.append(int(bundle_id))
    jsonnn = json.dumps(y, default=obj_dict)
    connection.execute(f'UPDATE users SET available_bundles = "{jsonnn}" WHERE id = {user_id}')
    connection.commit()


def obj_dict(obj):
    return obj.__dict__


class Bundle:
    bundle_id: int
    created_date: str
    author_id: int
    name: str
    price: int
    company: str
    date_interview: str
    direction: str
    assembling: list

    def __init__(self, bundle_id, created_date, author_id, name, price, company, date_interview, direction, assembling):
        self.bundle_id = bundle_id
        self.created_date = created_date
        self.author_id = author_id
        self.name = name
        self.price = price
        self.company = company
        self.date_interview = date_interview
        self.direction = direction
        self.assembling = assembling


def get_all_bundles():
    bundless: list[tuple] = connection.execute("SELECT * FROM bundles").fetchmany(5)
    new_listt = []

    for t in bundless:
        new_listt.append(Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                                date_interview=t[6], direction=t[7], assembling=t[8]))

    return new_listt


def get_available_bundles_for_user(user_id: int):
    bundles_json: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[0]
    s = bundles_json.replace('[', '(').replace(']',')')
    bundless: list[tuple] = connection.execute(f'SELECT * FROM bundles WHERE id IN {s}').fetchmany(5)
    new_listt = []

    for t in bundless:
        new_listt.append(Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                                date_interview=t[6], direction=t[7], assembling=t[8]))

    return new_listt
