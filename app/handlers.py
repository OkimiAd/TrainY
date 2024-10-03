from typing import Union, Type

from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.database
import app.keyboards as kb





class Bundle(StatesGroup):
    creating = State()
    # items: Type[Union[TextMessage, DocumentMessage]]


# @router.message(CommandStart())
# async def on_start(message: types.Message, state: FSMContext):
#     await message.answer("on_start")
#     await state.set_state(Form.name)
    # user = message.from_user
    # await message.answer_sticker("CAACAgIAAxkBAAEM6fVm_qXxZ7ZxROUM-u_AIYJFa1zMGwAC6iMAAhvGAUqp6ktzFro9QjYE")
    #
    # await message.answer("Привет " + user.first_name)
    # await message.answer(
    #     "Это бот TrainY! Тут ты можешь найти свежие записи собеседований в любую компанию на любую должность.\nДля начала можешь перейти в список записей.\nДля всех новичков скидка 100% на первую покупку☺️",
    #     reply_markup=kb.main)
    #
    # app.database.add_user(user.id, user.username)
    # print("/start " + user.username)

@router.message(Form.name)
async def assembly_bundle(message: types.Message, state: FSMContext):
    await message.answer("assembly_bundle")


@router.message(Command("help"))
async def on_help(message: types.Message):
    user = message.from_user
    print("/help " + user.username)
    await on_FAQ(message)


@router.message(F.text == 'FAQ')
async def on_FAQ(message: types.Message):
    await message.answer("Тут ты найдешь подробную интструкию по тому что тут происходит", protect_content=True)
    await message.answer("1. Плати больше деняк")

    user = message.from_user

    print("FAQ " + user.username)


# @router.message()
# async def on_FAQ(message: types.Message):
#     await message.answer("Не понимаю тебя😅", protect_content=True)
#     user = message.from_user
#     print(message.text + user.username)
#

@router.message(F.text == 'Для авторов')
async def create_bundle(message: types.Message, state: FSMContext):
    await message.answer(
        "Записи распространяются в виде бандлов. "
        "Каждый бандл состоит из элементов текста, аудио или фото документов. "
        "Необходим добавить как минимум один из элементов. "
        "Для того что бы добавить новый элемент просто отправьте его новым сообщением. "
        "Фото обязательно присылать без сжатия")


    await state.set_state(Bundle.creating)
    await message.answer("Для того что бы завершить создание бандла отправье\n/commit")

    user = message.from_user
    print("Для авторов " + user.username)

