from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Каталог интервью"), KeyboardButton(text="Доступные мне")],
                               [KeyboardButton(text="Для авторов"), KeyboardButton(text="FAQ")],
                           ]
                           )

doesnt_matter = ReplyKeyboardMarkup(resize_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Не важно")],
                           ]
                           )

directions = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Android"), KeyboardButton(text="IOS")],
                               [KeyboardButton(text="Front-end"), KeyboardButton(text="Back_end")],
                           ]
                           )

moderate = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отправить на модерацию", callback_data="moderate"),
                      InlineKeyboardButton(text="Удалить", callback_data="delete")]])
