from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(resize_keyboard=True,
                           keyboard=[
                               [KeyboardButton(text="Каталог интервью"), KeyboardButton(text="Доступные мне")],
                               [KeyboardButton(text="Для авторов"), KeyboardButton(text="FAQ")],
                               [KeyboardButton(text="Подписка на поиск")]
                           ]
                           )

doesnt_matter = ReplyKeyboardMarkup(resize_keyboard=True,
                                    keyboard=[
                                        [KeyboardButton(text="Не важно")],
                                    ]
                                    )

directions = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                                 keyboard=[
                                     [KeyboardButton(text="Android"), KeyboardButton(text="IOS")],
                                     [KeyboardButton(text="Front-end"), KeyboardButton(text="Back_end")],
                                 ]
                                 )

subscribes = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [KeyboardButton(text="Мои подписки")],
                                     [KeyboardButton(text="Добавить подписку")]
                                 ]
                                 )

for_authors = ReplyKeyboardMarkup(resize_keyboard=True,
                                 keyboard=[
                                     [KeyboardButton(text="Выложить запись")],
                                     [KeyboardButton(text="Вывести деньги")]
                                 ]
                                 )

create_bundle = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отправить на модерацию", callback_data="moderate"),
                      InlineKeyboardButton(text="Удалить", callback_data="delete")]])

moderate = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Принять", callback_data="approve"),
                      InlineKeyboardButton(text="Отклонить", callback_data="reject")]])
