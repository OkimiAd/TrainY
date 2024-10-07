from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils import markdown

import app.database as db
import app.keyboards as kb

router = Router()

class DocumentMess:
    doc_id: int

    def __init__(self, f):
        self.doc_id = f

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
    choose_id_buy = State()
    filter_direction = State()
    filter_company = State()
    choose_id_open = State()


@router.message(F.text == 'Подписка на поиск')
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Это раздел настройки подписки на поиск. Вы можете выбрать компанию и направление которое вас интересует и вы будете получать уведомление о появлении новых записей сразу же как они появятся.",
        protect_content=True, reply_markup=kb.subscribes)


@router.message(F.text == 'Добавить подписку')
async def subscribe_search(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SubscribesFlow.add_sub_direction)
    await message.answer(
        "Какое направление программирования вас интересует",
        protect_content=True, reply_markup=kb.directions)


class SubscribesFlow(StatesGroup):
    add_sub_direction = State()
    add_sub_company = State()


@router.message(SubscribesFlow.add_sub_direction)
async def filter_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(SubscribesFlow.add_sub_company)
    await message.answer("Какая компания вас интересует?(Англ)", protect_content=True)


@router.message(SubscribesFlow.add_sub_company)
async def filter_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    state_data = await state.get_data()
    db.add_subscribe_search(direction=state_data["direction"],
                            company=state_data["company"], chat_id=message.chat.id)
    await message.answer("Подписка успешно добавлена", protect_content=True, reply_markup=kb.main)
    await state.clear()


@router.message()
async def other(message: types.Message):
    await message.answer("Не понимаю тебя😅", protect_content=True)
    user = message.from_user
    print(message.text + user.username)
