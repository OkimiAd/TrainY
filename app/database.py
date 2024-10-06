import datetime
import json
import sqlite3 as sq


# connection = sq.connect('database.db')
# cursor = connection.cursor()


async def db_start():
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
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
        # connection.commit()


def add_user(user_id: int, name: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        time = str(datetime.datetime.now())
        cursor.execute('INSERT OR IGNORE INTO users (id, date_added, name) VALUES (?, ?, ?)',
                       (user_id, time, name))
        connection.commit()


def add_bundle(*, author_id: int, name: str, price: int, company: str, date_interview: str, direction: str,
               assembly: list):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        created_date = str(datetime.datetime.now())
        cursor.execute(
            'INSERT OR REPLACE INTO bundles (created_date, author_id, name, price, company, date_interview, direction, assembling) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (created_date, author_id, name, price, company, date_interview, direction,
             json.dumps(assembly, default=obj_dict)))
        connection.commit()


def get_bundle(*, bundle_id):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'SELECT assembling FROM bundles WHERE id = {bundle_id}').fetchone()[0]


def add_bundle_for_user(*, user_id: int, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        original_list: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        if original_list == '"':
            original_list = "[]"
        y: list = json.loads(original_list)
        y.append(int(bundle_id))
        jsonnn = json.dumps(y, default=obj_dict)
        connection.execute(f'UPDATE users SET available_bundles = "{jsonnn}" WHERE id = {user_id}')
        connection.commit()


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


# id NOT IN {s} AND
def get_filtered_bundles(user_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[0]
        s = bundles_json.replace('[', '(').replace(']', ')')

        company_str:str
        if company == "Не важно":
            company_str= ""
        else:
            company_str=f'AND company = "{company}" COLLATE NOCASE'

        exe = f'SELECT * FROM bundles WHERE direction = "{direction}" COLLATE NOCASE {company_str} AND id NOT IN {s} ORDER BY id DESC'
        bundless: list[tuple] = cursor.execute(exe).fetchmany(5)
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))
        return new_listt


def user_have_bundle_access(user_id: int, bundle_id: int) -> bool:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        bundle_id_list: list = json.loads(bundles_json)
        return bundle_id_list.__contains__(bundle_id)
        # s = bundles_json.replace('[', '(').replace(']', ')')
        # bundless: list[tuple] = connection.execute(
        #     f'SELECT * FROM bundles WHERE id NOT IN {s} ORDER BY id DESC').fetchmany(5)
        # new_listt = []
        #
        # for t in bundless:
        #     new_listt.append(Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
        #                             date_interview=t[6], direction=t[7], assembling=t[8]))

        # return new_listt


def get_available_bundles_for_user(user_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        s = bundles_json.replace('[', '(').replace(']', ')')
        bundless: list[tuple] = connection.execute(f'SELECT * FROM bundles WHERE id IN {s}').fetchmany(10)
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))

        return new_listt


def obj_dict(obj):
    return obj.__dict__
