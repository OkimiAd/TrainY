from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Доступные мне"), KeyboardButton(text="Список записей")],
                               [KeyboardButton(text="Для авторов"), KeyboardButton(text="FAQ")],
                           ]
                           )
