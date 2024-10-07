import sqlite3 as sq

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
                       "is_moderated BIT DEFAULT 0"
                       ")"
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
                       "phone TEXT,"
                       "request_data TEXT)"
                       )


def add_subscribe_search(*, chat_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO subscribes (chat_id, company, direction) VALUES (?, ?, ?)',
            (chat_id, company, direction))

def add_money_request(*, chat_id: int, company: str, direction: str):
    with sq.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO subscribes (chat_id, company, direction) VALUES (?, ?, ?)',
            (chat_id, company, direction))
