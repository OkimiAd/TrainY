import datetime
import sqlite3

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('database.db')
cursor = connection.cursor()


async def db_start():
    cursor.execute("CREATE TABLE IF NOT EXISTS users("
                   "id INTEGER PRIMARY KEY,"
                   "date_added TEXT,"
                   "name TEXT)"
                   # "linkList JSON DEFAULT('[]'))"
                   )
    connection.commit()


def add_user(user_id: int, name: str):
    time = str(datetime.datetime.now())
    cursor.execute('INSERT OR REPLACE INTO users (id, date_added, name) VALUES (?, ?, ?)',
                   (user_id, time, name))
    connection.commit()

# # Удаляем пользователя "newuser"
# cursor.execute('DELETE FROM Users WHERE username = ?', ('newuser',))
#
# # Сохраняем изменения и закрываем соединение
# connection.commit()
# connection.close()
