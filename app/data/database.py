import sqlite3 as sq

from app.data.entities import MoneyRequest


def db_start():
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users("
                       "id INTEGER PRIMARY KEY,"
                       "date_added TEXT,"
                       "name TEXT,"
                       "cash INTEGER DEFAULT 0 ,"
                       "commission INTEGER DEFAULT 30 ,"
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
                       "is_moderated BIT DEFAULT 0,"
                       "bought_count INTEGER DEFAULT 0,"
                       "earned INTEGER DEFAULT 0)"
                       )

        cursor.execute("CREATE TABLE IF NOT EXISTS subscribes("
                       "id INTEGER PRIMARY KEY,"
                       "chat_id TEXT,"
                       "company TEXT,"
                       "direction TEXT)"
                       )

        cursor.execute("CREATE TABLE IF NOT EXISTS money_requests("
                       "id INTEGER PRIMARY KEY,"
                       "user_id TEXT,"
                       "for_author INTEGER,"
                       "commission INTEGER,"
                       "ndfl INTEGER,"
                       "request_data TEXT,"
                       "created_date TEXT DEFAULT CURRENT_TIMESTAMP,"
                       "status INTEGER DEFAULT 0"
                       ")"
                       )


def add_subscribe_search(*, chat_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO subscribes (chat_id, company, direction) VALUES (?, ?, ?)',
            (chat_id, company, direction))


def get_subscribes_for_user(*, chat_id: int) -> list[tuple]:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'SELECT * FROM subscribes WHERE chat_id = {chat_id}').fetchall()


def delete_subscribe(*, sub_id: int, chat_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'DELETE FROM subscribes WHERE chat_id = {chat_id} AND id = {sub_id}').fetchall()


def delete_all_subscribes(*, chat_id: int):
    list_subs = get_subscribes_for_user(chat_id=chat_id)
    for sub in list_subs:
        delete_subscribe(chat_id=chat_id, sub_id=sub[0])


def add_money_request(*, user_id: int, request_data: str, for_author: int, commission: int, ndfl: int, ):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO money_requests (user_id, request_data, for_author, commission, ndfl) VALUES (?, ?, ?, ?, ?)',
            (user_id, request_data, for_author, commission, ndfl))


def get_money_requests() -> list[MoneyRequest]:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        exe = f'SELECT * FROM money_requests ORDER BY created_date ASC'
        bundless: list[tuple] = cursor.execute(exe).fetchall()
        new_listt = []

        for t in bundless:
            new_listt.append(
                MoneyRequest(id=t[0], user_id=t[1], for_author=t[2], commission=t[3], ndfl=t[4], request_date=t[5],
                             created_date=t[6]))
        return new_listt


def is_user_have_money_request(*, user_id: int, ) -> bool:
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        id_money_req = cursor.execute(f'SELECT id FROM money_requests WHERE user_id = {user_id}').fetchone()
        return id_money_req is not None

# def delete_money_request(*, mr_id: int):
#     with sq.connect("database.db") as connection:
#         cursor = connection.cursor()
#         return cursor.execute(f'DELETE FROM money_requests WHERE id = {mr_id}')

def set_money_request_status(*, mr_id: int):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        return cursor.execute(f'DELETE FROM money_requests WHERE id = {mr_id}')

