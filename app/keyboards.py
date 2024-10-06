from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Каталог интервью"), KeyboardButton(text="Доступные мне")],
                               [KeyboardButton(text="Для авторов"), KeyboardButton(text="FAQ")],
                           ]
                           )

moderate = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отправить на модерацию", callback_data="moderate"),
                      InlineKeyboardButton(text="Удалить", callback_data="delete")]])
