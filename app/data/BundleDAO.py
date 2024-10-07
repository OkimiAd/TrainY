import json
import sqlite3 as sq
from datetime import datetime

from app.data.UserDAO import credit_to_the_author
from app.data.entities import Bundle
from main import bot


def create_bundle(*, author_id: int, name: str, price: int, company: str, date_interview: str, direction: str,
                  assembly: list):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        created_date = str(datetime.now())
        cursor.execute(
            'INSERT OR REPLACE INTO bundles (created_date, author_id, name, price, company, date_interview, direction, assembling) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (created_date, author_id, name, price, company, date_interview, direction,
             json.dumps(assembly, default=obj_dict)))

def delete_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'DElETE FROM bundles WHERE id = "{bundle_id}"')

async def approve_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE bundles SET is_moderated = "1" WHERE id = "{bundle_id}"')

        await initiate_mailing(bundle_id=bundle_id)

async def initiate_mailing(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()

        bundle = get_bundle(bundle_id=bundle_id)

        chat_list: list[tuple] = cursor.execute(
            f'SELECT chat_id FROM subscribes WHERE company = "{bundle.company}" COLLATE NOCASE AND direction = "{bundle.direction}" COLLATE NOCASE').fetchall()

        for chat in chat_list:
            chat_id: str = chat[0]
            await bot.send_message(chat_id=chat_id, text="По вашей подписке есть новая запись",
                                   protect_content=True)
            await bot.send_message(chat_id=chat_id,
                                   text=f'id - {bundle_id}\n{bundle.name}\n{bundle.company}\n{bundle.direction}\n{bundle.date_interview}\n{bundle.price}₽',
                                   protect_content=True)
            await bot.send_message(chat_id=chat_id, text="Для того что бы купить напиши /buy_bundle",
                                   protect_content=True)



def get_bundle_assembling(*, bundle_id):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'SELECT assembling FROM bundles WHERE id = {bundle_id}').fetchone()[0]


def get_bundle(*, bundle_id) -> Bundle:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()

        tup: tuple = cursor.execute(f'SELECT * FROM bundles WHERE id = {bundle_id}').fetchone()

        bundle = Bundle(bundle_id=tup[0], created_date=tup[1], author_id=tup[2], name=tup[3], price=tup[4],
                        company=tup[5],
                        date_interview=tup[6], direction=tup[7], assembling=tup[8])
        return bundle

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

    bundle = get_bundle(bundle_id=bundle_id)
    credit_to_the_author(bundle.author_id, bundle.price)

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

def get_available_bundles_for_user(user_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = connection.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        s = bundles_json.replace('[', '(').replace(']', ')')
        bundless: list[tuple] = connection.execute(f'SELECT * FROM bundles WHERE id IN {s} ORDER BY id DESC').fetchmany(
            10)
        new_listt = []

        for t in bundless:
            new_listt.append(
                Bundle(bundle_id=t[0], created_date=t[1], author_id=t[2], name=t[3], price=t[4], company=t[5],
                       date_interview=t[6], direction=t[7], assembling=t[8]))

        return new_listt

def obj_dict(obj):
    return obj.__dict__
