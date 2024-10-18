import json
import sqlite3 as sq
from datetime import datetime

from googletrans import Translator

from app.data.UserDAO import credit_to_the_user
from app.data.entities import Bundle, parse_bundle
from my_bot import bot


def create_bundle(*, author_id: int, name: str, price: int, company: str, date_interview: str, direction: str,
                  assembly: list):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        created_date = str(datetime.now())
        cursor.execute(
            'INSERT OR REPLACE INTO bundles (created_date, author_id, name, price, company, date_interview, direction, assembling) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (created_date, author_id, name, price, company, date_interview, direction,
             json.dumps(assembly, default=obj_dict)))

        original_list: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {author_id}').fetchone()[
            0]
        if original_list == '"':
            original_list = "[]"
        y: list = json.loads(original_list)
        y.append(cursor.lastrowid)
        jsonnn = json.dumps(y, default=obj_dict)
        cursor.execute(f'UPDATE users SET available_bundles = "{jsonnn}" WHERE id = {author_id}')


def reject_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE bundles SET is_moderated = "rejected" WHERE id = "{bundle_id}"')
        # cursor.execute(f'DElETE FROM bundles WHERE id = "{bundle_id}"')


async def approve_bundle(*, bundle_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'UPDATE bundles SET is_moderated = "approved" WHERE id = "{bundle_id}"')

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

        bundle = parse_bundle(tup)
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

        bought_count_earned_price = cursor.execute(
            f'SELECT bought_count, earned, price FROM bundles WHERE id = {bundle_id}').fetchone()
        cursor.execute(f'UPDATE bundles SET '
                       f'bought_count = "{bought_count_earned_price[0] + 1}", '
                       f'earned = "{bought_count_earned_price[1] + bought_count_earned_price[2]}" '
                       f' WHERE id = {bundle_id}')
    bundle = get_bundle(bundle_id=bundle_id)
    credit_to_the_user(user_id=bundle.author_id, cash=bundle.price)


def get_filtered_bundles(user_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[0]
        s = bundles_json.replace('[', '(').replace(']', ')')

        company_str: str
        if company == "Не важно":
            company_str = ""
        else:
            translator = Translator()
            translation = translator.translate(company, 'en')
            company_str = (f'AND company LIKE \'%{company}%\' COLLATE NOCASE OR'
                           f' company LIKE \'%{translation.text}%\' COLLATE NOCASE')

        exe = f'SELECT * FROM bundles WHERE direction = "{direction}" COLLATE NOCASE {company_str} AND id NOT IN {s} AND is_moderated = "approved" ORDER BY id DESC'
        bundless: list[tuple] = cursor.execute(exe).fetchmany(10)
        new_listt = []

        for t in bundless:
            new_listt.append(parse_bundle(t))
        return new_listt


def get_not_moderated_bundle() -> list[Bundle]:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        exe = f'SELECT * FROM bundles WHERE is_moderated = "new" ORDER BY id ASC'
        bundless: list[tuple] = cursor.execute(exe).fetchall()
        new_listt = []

        for t in bundless:
            new_listt.append(parse_bundle(t))
        return new_listt


def get_available_bundles_for_user(user_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        s = bundles_json.replace('[', '(').replace(']', ')')
        bundless: list[tuple] = cursor.execute(f'SELECT * FROM bundles WHERE id IN {s} ORDER BY id DESC').fetchall()
        new_listt = []

        for t in bundless:
            new_listt.append(parse_bundle(t))

        return new_listt


def get_bundles_for_author(author_id: int) -> list[Bundle]:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_list_tuple = cursor.execute(
            f'SELECT * FROM bundles WHERE author_id = {author_id} ORDER BY id DESC').fetchall()
        new_listt = []
        for t in bundles_list_tuple:
            new_listt.append(parse_bundle(t))

        return new_listt


def obj_dict(obj):
    return obj.__dict__
