import json

from aiogram import types, Router, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils import markdown

import app.database as db
import app.keyboards as kb
from my_bot import bot

router = Router()


class DocumentMess:
    doc_id: int

    def __init__(self, f):
        self.doc_id = f


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
    await message.answer("Возвращение в начало чата")
    await state.clear()


class AdminFlow(StatesGroup):
    password = State()
    in_admin = State()
    moderate = State()
    reject = State()


@router.message(Command('admin'))
async def on_admin(message: types.Message, state: FSMContext):
    await state.set_state(AdminFlow.password)
    await message.answer("Введите пароль для входа в админку")


@router.message(AdminFlow.password)
async def on_admin(message: types.Message, state: FSMContext):
    if message.text == "1234":
        await message.answer("Вы успешно вошли в админку")
        await message.answer("/moderate_bundle - для того что бы увидеть ожидающий бандл")
        await state.set_state(AdminFlow.in_admin)
    else:
        await message.answer("Не верный пароль")
        await state.clear()


@router.message(Command('moderate_bundle'))
async def moderate_bundle(message: types.Message, state: FSMContext):
    if await state.get_state() != str(AdminFlow.in_admin.state):
        await message.answer(f'Доступ запрещен')
        return

    list_bundles = db.get_not_moderated_bundle()
    await message.answer(f'На модерации - {len(list_bundles)}')

    if len(list_bundles) == 0:
        return

    item = list_bundles[0]
    await message.answer(
        f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
        f'{item.direction} - {item.company} - {item.date_interview}')

    await state.set_state(AdminFlow.moderate)
    await state.update_data(bundle=item)
    listt = db.get_bundle(bundle_id=item.bundle_id)
    y: list = json.loads(listt)
    for i in y:
        if type(i) is dict:
            await message.answer_document(i["doc_id"])
        else:
            await message.answer(i)

    await message.answer(f'/approve - принять\n'
                         f'/reject - отклонить')


@router.message(Command('approve'))
async def on_admin(message: types.Message, state: FSMContext):
    if await state.get_state() != str(AdminFlow.moderate.state):
        await message.answer(f'Доступ запрещен')
        return
    await message.answer(f'Принято')
    state_data = await state.get_data()
    db.approve_bundle(bundle_id=state_data["bundle"].bundle_id)

    await bot.send_message(chat_id=state_data["bundle"].author_id,
                           text=f'Ваш Bundle id - {state_data["bundle"].bundle_id} был принят')

    await state.set_state(AdminFlow.in_admin)
    await moderate_bundle(message, state)


@router.message(Command('reject'))
async def on_admin(message: types.Message, state: FSMContext):
    if await state.get_state() != str(AdminFlow.moderate.state):
        await message.answer(f'Доступ запрещен')
        return
    await message.answer(f'Напишите причину отказа')
    await state.set_state(AdminFlow.reject)


@router.message(AdminFlow.reject)
async def on_admin(message: types.Message, state: FSMContext):
    await message.answer(f'Отклонено')
    #     удаляем из бд но сначала уведомляем пользователя и отправляем развернутый бандл
    state_data = await state.get_data()
    await bot.send_message(chat_id=state_data["bundle"].author_id,
                           text=f'Ваш Bundle id - {state_data["bundle"].bundle_id} был отклонен')

    await bot.send_message(chat_id=state_data["bundle"].author_id,
                           text=f'Причина - {message.text}')

    db.delete_bundle(bundle_id=state_data["bundle"].bundle_id)

    await state.set_state(AdminFlow.in_admin)
    await moderate_bundle(message, state)


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
