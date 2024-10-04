from aiogram import types, Router, F
from aiogram.enums import ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

import app.database as db
import app.keyboards as kb

router = Router()


class DocumentMess:
    doc_id: int

    def __init__(self, f):
        self.doc_id = f


class Bundle(StatesGroup):
    assembly = State()
    name = State()
    price = State()
    company = State()
    date = State()
    direction = State()


@router.message(CommandStart())
async def on_start(message: types.Message, state: FSMContext):
    user = message.from_user
    await message.answer_sticker("CAACAgIAAxkBAAEM6o9m_xXrhAqbSSVi3qlJF-avCUEN0AACSB0AAuIkgEot-Nk2wyVajjYE")

    await message.answer("Привет " + user.first_name)
    await message.answer(
        "Это бот TrainY! Тут ты можешь найти свежие записи собеседований в любую компанию на любую должность.\nДля начала можешь перейти в список записей.\nДля всех новичков скидка 100% на первую покупку☺️",
        reply_markup=kb.main)

    db.add_user(user.id, user.username)
    await state.clear()
    print("/start " + user.username)


@router.message(Command('cancel'))
async def on_cancel(message: types.Message, state: FSMContext):
    await state.clear()


@router.message(F.text == 'FAQ')
async def on_FAQ(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Тут ты найдешь подробную интструкию по тому что тут происходит", protect_content=True)
    await message.answer("1. Плати больше деняк")

    user = message.from_user

    print("FAQ " + user.username)


@router.message(F.text == 'Для авторов')
async def for_authors(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Записи распространяются в виде бандлов. "
        "Каждый бандл состоит из элементов текста, аудио или фото документов. "
        "Необходим добавить как минимум один из элементов. "
        "Для того что бы добавить новый элемент просто отправь его новым сообщением. "
        "Фото обязательно присылать без сжатия")

    await message.answer("Для того что бы завершить создание бандла отправье\n/commit")

    await state.set_state(Bundle.assembly)

    user = message.from_user
    print("Для авторов " + user.username)


@router.message(Bundle.assembly)
async def assembly_bundle(message: types.Message, state: FSMContext):
    if message.text == '/commit':
        print('/commit')
        await message.answer("Бандл успешно собран")
        await message.answer("Теперь введи название бандла")
        await state.set_state(Bundle.name)
    else:
        data = await state.get_data()
        list_elements = data.get("assembly", [])

        if message.content_type is ContentType.TEXT:
            list_elements.append(message.text)
        elif message.content_type is ContentType.DOCUMENT:
            list_elements.append(DocumentMess(message.document.file_id))
        else:
            await message.answer("Этот формат не поддерживается в бандде")
        await state.update_data(assembly=list_elements)


@router.message(Bundle.name)
async def name_bundle(message: types.Message, state: FSMContext):
    user = message.from_user
    print("name_bundle " + user.username + " " + message.text)

    await state.update_data(name=message.text)

    await message.answer("Название добавлено")
    await message.answer("Теперь введи стоимость в рублях(только число, без доп символов)")
    await state.set_state(Bundle.price)


@router.message(Bundle.price)
async def price_bundle(message: types.Message, state: FSMContext):
    user = message.from_user
    print("price_bundle " + user.username + " " + message.text)

    await state.update_data(price=message.text)

    await message.answer("Ценник обновлен")
    await message.answer("Введи название компании")
    await state.set_state(Bundle.company)


@router.message(Bundle.company)
async def company_name_bundle(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(Bundle.date)
    await message.answer("Введи дату собеседования в формате dd.MM.yyyy")


@router.message(Bundle.date)
async def date_bundle(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(Bundle.direction)
    await message.answer("Какое направление? BackEnd, FrontEnd и другие")


@router.message(Bundle.direction)
async def grade_bundle(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await end_assembling(message, state)


async def end_assembling(message: types.Message, state: FSMContext):
    await message.answer(f'Данные записаны и вот так они будут выглядеть для покупателя')
    data = await state.get_data()
    listt = data["assembly"]
    for i in listt:
        if type(i) is DocumentMess:
            await message.answer_document(i.doc_id)
        else:
            await message.answer(i)
    await message.answer('А в каталоге вакансий будет выглядеть так')
    await message.answer(f'{data["name"]}\n{data["company"]}\n{data["direction"]}\n{data["date"]}\n{data["price"]}₽',
                         reply_markup=kb.moderate)


@router.callback_query(F.data == "moderate")
async def callback_query(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    db.add_bundle(author_id=callback.from_user.id,
                  name=data["name"],
                  price=data["price"],
                  company=data["company"],
                  date_interview=data["date"],
                  direction=data["direction"],
                  assembly=data["assembly"],
                  )


    # dd = data["name"]
# await callback.message.answer('moderate')
# await callback.message.answer(dd)


@router.message()
async def other(message: types.Message):
    await message.answer("Не понимаю тебя😅", protect_content=True)
    user = message.from_user
    print(message.text + user.username)
