import datetime
import json
import sqlite3 as sq

from main import bot

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
                       "assembling JSON,"
                       "is_moderated BIT"
                       ")"
                       )

        cursor.execute("CREATE TABLE IF NOT EXISTS subscribes("
                       "id INTEGER PRIMARY KEY,"
                       "user_id TEXT,"
                       "company TEXT,"
                       "direction TEXT)"
                       )


def add_user(user_id: int, name: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        time = str(datetime.datetime.now())
        cursor.execute('INSERT OR IGNORE INTO users (id, date_added, name) VALUES (?, ?, ?)',
                       (user_id, time, name))
        connection.commit()


async def create_bundle(*, author_id: int, name: str, price: int, company: str, date_interview: str, direction: str,
                        assembly: list):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        created_date = str(datetime.datetime.now())
        cursor.execute(
            'INSERT OR REPLACE INTO bundles (created_date, author_id, name, price, company, date_interview, direction, assembling) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (created_date, author_id, name, price, company, date_interview, direction,
             json.dumps(assembly, default=obj_dict)))

        # await initiate_mailing(company, direction, cursor.lastrowid, name, price, date_interview)


async def initiate_mailing(company: str, direction: str, bundle_id, name: str, price: int, date_interview: str,):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        chat_list: list[tuple] = cursor.execute(
            f'SELECT chat_id FROM subscribes WHERE company = "{company}" COLLATE NOCASE AND direction = "{direction}" COLLATE NOCASE').fetchall()

        for chat in chat_list:
            chat_id: str = chat[0]
            await bot.send_message(chat_id=chat_id, text="По вашей подписке есть новая запись",
                                   protect_content=True)
            await bot.send_message(chat_id=chat_id,
                                   text=f'id - {bundle_id}\n{name}\n{company}\n{direction}\n{date_interview}\n{price}₽',
                                   protect_content=True)
            await bot.send_message(chat_id=chat_id, text="Для того что бы купить напиши /buy_bundle",
                                   protect_content=True)


def get_bundle(*, bundle_id):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'SELECT assembling FROM bundles WHERE id = {bundle_id}').fetchone()[0]


def buy_bundle(*, user_id: int, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        original_list: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        if original_list == '"':
            original_list = "[]"
        y: list = json.loads(original_list)
        y.append(int(bundle_id))
        jsonnn = json.dumps(y, default=obj_dict)
        cursor.execute(f'UPDATE users SET available_bundles = "{jsonnn}" WHERE id = {user_id}')

def approve_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE bundles SET is_moderated = "1" WHERE id = "{bundle_id}"')

def delete_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'DElETE FROM bundles WHERE id = "{bundle_id}"')


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

        company_str: str
        if company == "Не важно":
            company_str = ""
        else:
            company_str = f'AND company = "{company}" COLLATE NOCASE'

        exe = f'SELECT * FROM bundles WHERE direction = "{direction}" COLLATE NOCASE {company_str} AND id NOT IN {s} AND is_moderated = 1 ORDER BY id DESC'
        bundless: list[tuple] = cursor.execute(exe).fetchmany(10)
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))
        return new_listt

def get_not_moderated_bundle():
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        exe = f'SELECT * FROM bundles WHERE is_moderated = 0 ORDER BY id ASC'
        bundless: list[tuple] = cursor.execute(exe).fetchall()
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))
        return new_listt


def user_have_bundle_access(user_id: int, bundle_id: int) -> bool:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        bundle_id_list: list = json.loads(bundles_json)
        return bundle_id_list.__contains__(bundle_id)


def add_subscribe_search(*, chat_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO subscribes (chat_id, company, direction) VALUES (?, ?, ?)',
            (company, direction, chat_id))


def get_available_bundles_for_user(user_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        s = bundles_json.replace('[', '(').replace(']', ')')
        bundless: list[tuple] = connection.execute(f'SELECT * FROM bundles WHERE id IN {s} ORDER BY id DESC').fetchmany(10)
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))

        return new_listt


def obj_dict(obj):
    return obj.__dict__
