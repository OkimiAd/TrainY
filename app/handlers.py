
from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils import markdown

import app.database as db
import app.keyboards as kb

router = Router()


@router.message(CommandStart())
async def on_start(message: types.Message, state: FSMContext):
    user = message.from_user

    await message.answer_sticker("CAACAgIAAxkBAAEM6o9m_xXrhAqbSSVi3qlJF-avCUEN0AACSB0AAuIkgEot-Nk2wyVajjYE")

    await message.answer("Привет " + user.first_name)
    await message.answer(
        "Это бот TrainY! Тут ты можешь найти свежие записи собеседований в любую компанию на любую должность.\n"
        "Для начала можешь перейти в каталог интервью.☺️",
        reply_markup=kb.main)

    db.add_user(user.id, user.username)
    await state.clear()


@router.message(Command('cancel'))
async def on_cancel(message: types.Message, state: FSMContext):
    await state.clear()


@router.message(F.text == 'FAQ')
async def on_FAQ(message: types.Message, state: FSMContext):
    await state.clear()

    text = markdown.text(
        "С помощью этих инструментов ты можешь записывать свои собеседования:",
        "\n",
        "*Windows*",
        "Xbox Game Bar",
        "OBS Studio",
        "bandicam",
        "NVIDIA ShadowPlay",
        "\n",
        "*MacOS*",
        "OBS Studio",
        "SurFlex Screen Recorder",
        "\n",
        "*Telegram*",
        "1 \- Создать группу в телеграм на себя одного",
        "2 \- Включить видеовстречу с демонстрацией экрана и там включить запись",
        "Пишет сразу в хорошем разрешение с захватом звука и сохраняет в избранное в самом телеграме",
        sep="\n"
    )

    await message.answer(text, protect_content=True, parse_mode=ParseMode.MARKDOWN_V2)


class CatalogFlow(StatesGroup):
    choose_id = State()


@router.message(F.text == 'Каталог интервью')
async def on_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    list_bundles = db.get_all_bundles()
    await message.answer("Для того что бы купить напиши id интересующего тебя bundle", protect_content=True)

    await state.set_state(CatalogFlow.choose_id)

    for item in list_bundles:
        await message.answer(
            f'id - {item.bundle_id}\n{item.name}\n{item.company}\n{item.direction}\n{item.date_interview}\n{item.price}₽')


@router.message(CatalogFlow.choose_id)
async def date_bundle(message: types.Message, state: FSMContext):
    db.add_bundle_for_user(user_id=message.from_user.id, bundle_id=int(message.text))
    await state.clear()
    await message.answer("Bundle успешно куплен. Теперь ты его можешь найти в разделе \"Доступные мне\"")


@router.message(F.text == 'Доступные мне')
async def on_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    list_bundles = db.get_available_bundles_for_user(user_id=message.from_user.id)
    # await message.answer("Для того что бы купить напиши id интересующего тебя bundle", protect_content=True)

    # await state.set_state(CatalogFlow.choose_id)

    for item in list_bundles:
        await message.answer(
            f'id - {item.bundle_id}\n{item.name}\n{item.company}\n{item.direction}\n{item.date_interview}\n{item.price}₽')


@router.message()
async def other(message: types.Message):
    await message.answer("Не понимаю тебя😅", protect_content=True)
    user = message.from_user
    print(message.text + user.username)
