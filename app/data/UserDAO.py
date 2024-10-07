import json
import sqlite3 as sq
from datetime import datetime

from app.data.entities import User


def add_user(user_id: int, name: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        time = str(datetime.now())
        cursor.execute('INSERT OR IGNORE INTO users (id, date_added, name) VALUES (?, ?, ?)',
                       (user_id, time, name))
        connection.commit()

def get_user(*, user_id) -> User:
    print("get_user_start")
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()

        tup: tuple = cursor.execute(f'SELECT * FROM users WHERE id = {user_id}').fetchone()

        print("get_user_end")
        return User(id=tup[0], date_added=tup[1], name=tup[2], cash=tup[3], commission=tup[4],
                    available_bundles=tup[5], )

def credit_to_the_author(author_id: int, cash: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        original_cash: int = cursor.execute(f'SELECT cash FROM users WHERE id = {author_id}').fetchone()[0]
        cursor.execute(f'UPDATE users SET cash = {original_cash + cash} WHERE id = {author_id}')

def is_user_have_bundle_access(user_id: int, bundle_id: int) -> bool:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        bundles_json: str = cursor.execute(f'SELECT available_bundles FROM users WHERE id = {user_id}').fetchone()[
            0]
        bundle_id_list: list = json.loads(bundles_json)
        return bundle_id_list.__contains__(bundle_id)