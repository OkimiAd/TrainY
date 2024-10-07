import time

from aiogram import types, Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

import app.data.database as db
import app.keyboards as kb
from app.handlers import DocumentMess
import app.data.BundleDAO as daoBundle
import app.data.UserDAO as daoUser

router = Router()


class GetMoney(StatesGroup):
    get_money = State()
    get_transfer_data = State()


class Bundle(StatesGroup):
    assembly = State()
    name = State()
    price = State()
    company = State()
    date_interview = State()
    direction = State()


@router.message(F.text == 'Для авторов')
async def for_authors(message: types.Message, state: FSMContext):
    await message.answer(
        "Это раздел для для тех кто хочет выкладывать свои записи собеседований и зарабатывать на этом. "
        "Если ты прошел собеседовани, но тебе не дали офер, ты можешь заработать на том что подробная информация про вопросы на собесе сильно поможет следующим соискателям, "
        "и они прямо как и ты готовы заплатить за эту информацию.", reply_markup=kb.for_authors)


@router.message(F.text == 'Вывести деньги')
async def withdraw_money(message: types.Message, state: FSMContext):
    user = daoUser.get_user(user_id=message.from_user.id)
    await message.answer(f'*{user.cash}₽* Вам удалось заработать на данный момент🤑', parse_mode=ParseMode.MARKDOWN_V2)
    if user.cash < 1000:
        await message.answer(f'Вывести можно минимум 1000₽. Вам вывод пока что не доступен')
    else:
        await message.answer(f'Для того что бы вывести деньги введите\n/get_money')


@router.message(Command('get_money'))
async def withdraw_money(message: types.Message, state: FSMContext):
    user = daoUser.get_user(user_id=message.from_user.id)
    if user.cash < 1000:
        await message.answer(f'Вывод не доступен, потому что у вас меньше минимальной суммы вывода')
        return
    await state.set_state(GetMoney.get_money)
    await message.answer(f'Сколько вы хотите вывести?')


@router.message(GetMoney.get_money)
async def withdraw_money(message: types.Message, state: FSMContext):
    user = daoUser.get_user(user_id=message.from_user.id)
    if int(message.text) > user.cash:
        await message.answer(f'Недостаточно средств. Введите еще раз')
        return
    await state.update_data(money=int(message.text))
    await state.set_state(GetMoney.get_transfer_data)
    await message.answer(
        f'Введите номер телефона, имя и банк куда необходимо отправить перевод. Если информация будет некорректная заявка будет отклонена')


@router.message(GetMoney.get_transfer_data)
async def withdraw_money(message: types.Message, state: FSMContext):
    # message.text
    # db add money request
    await message.answer(f'Заявка отправлена и будет обработана в течении 7 рабочих дней')


@router.message(F.text == 'Выложить запись')
async def create_bundle(message: types.Message, state: FSMContext):
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
        await message.answer("Теперь введи название бандла(Англ)")
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

    await message.answer("Введи название компании")
    await state.set_state(Bundle.company)


@router.message(Bundle.company)
async def company_name_bundle(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(Bundle.date_interview)
    await message.answer("Введи дату собеседования в формате dd.MM.yyyy")


@router.message(Bundle.date_interview)
async def date_bundle(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(Bundle.direction)
    await message.answer("Какое направление? BackEnd, FrontEnd и другие", reply_markup=kb.directions)


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
                         reply_markup=kb.create_bundle)


@router.callback_query(F.data == "moderate")
async def callback_query(callback: CallbackQuery, state: FSMContext):
    if await state.get_state() != str(Bundle.direction.state):
        print("canceled")
        return

    data = await state.get_data()
    await callback.message.answer(
        'Ваш bundle успешно отправлен на модерацию. Когда он пройдет или не пройдет модерацию, вам будет направленно уведомление.',
        reply_markup=kb.main)

    await daoBundle.create_bundle(author_id=callback.from_user.id,
                           name=data["name"],
                           price=data["price"],
                           company=data["company"],
                           date_interview=data["date"],
                           direction=data["direction"],
                           assembly=data["assembly"],
                           )
    time.sleep(2)
    # await on_start(callback.message, state)
    await state.clear()
