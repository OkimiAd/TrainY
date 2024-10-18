import time

from aiogram import types, Router, F
from aiogram.enums import ContentType, ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery

import app.keyboards as kb
from app.handlers import DocumentMess
import app.data.BundleDAO as daoBundle
import app.data.UserDAO as daoUser
import app.data.database as db

router = Router()

commission_const = 10
min_sum_withdrawal = 5000


class GetMoney(StatesGroup):
    get_money = State()
    get_transfer_data = State()


class Bundle(StatesGroup):
    assembly = State()
    name = State()
    price = State()
    company = State()
    date_interview = State()
    type = State()
    direction = State()


@router.message(F.text == 'Для авторов')
async def for_authors(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    await message.answer(
        "Это раздел для для тех кто хочет выкладывать свои записи собеседований и зарабатывать на этом. "
        "Если ты прошел собеседовани, но тебе не дали офер, ты можешь заработать на том что подробная информация про вопросы на собесе сильно поможет следующим соискателям, "
        "и они прямо как и ты готовы заплатить за эту информацию.", reply_markup=kb.for_authors)


@router.message(F.text == 'Вывести деньги')
async def withdraw_money(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    user = daoUser.get_user(user_id=message.from_user.id)
    await message.answer(f'*{user.cash}₽* Вам удалось заработать на данный момент🤑', parse_mode=ParseMode.MARKDOWN_V2)
    await message.answer(f'Комиссия платформы составляет {commission_const}% \+ 13% НДФЛ',
                         parse_mode=ParseMode.MARKDOWN_V2)
    is_user_have_money_request = db.is_user_have_money_request(user_id=message.from_user.id)
    if is_user_have_money_request:
        await message.answer(f'У вас уже есть активная заявка на вывод средств. Подождите пока она обработается')
    elif user.cash < min_sum_withdrawal:
        await message.answer(f'Вывести можно минимум {min_sum_withdrawal}₽. Вам вывод пока что не доступен')
    else:
        await message.answer(f'Для того что бы вывести деньги введите\n/get_money')


@router.message(Command('get_money'))
async def withdraw_money(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    user = daoUser.get_user(user_id=message.from_user.id)
    is_user_have_money_request = db.is_user_have_money_request(user_id=message.from_user.id)
    if is_user_have_money_request:
        await message.answer(f'У вас уже есть активная заявка на вывод средств. Подождите пока она обработается')
        return
    elif user.cash < min_sum_withdrawal:
        await message.answer(f'Вывод не доступен, потому что у вас меньше минимальной суммы вывода')
        return
    await state.set_state(GetMoney.get_money)
    await message.answer(f'Сколько вы хотите вывести?')


@router.message(GetMoney.get_money)
async def withdraw_money(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    user = daoUser.get_user(user_id=message.from_user.id)
    if int(message.text) > user.cash:
        await message.answer(f'Недостаточно средств. Введите еще раз')
        return
    elif int(message.text) < min_sum_withdrawal:
        await message.answer(f'Можно вывести минимум {min_sum_withdrawal}')
        return

    commission = int(float(message.text) / 100 * commission_const)
    ndfl = int((int(message.text) - commission) / 100 * 13)
    for_author = int(message.text) - commission - ndfl

    await message.answer(
        f'Итого к выводу {message.text}₽ - {commission}₽ (комиссия {commission_const}%) - {ndfl}₽ (НДФЛ 13%) = {for_author}₽')

    await state.update_data(commission=commission)
    await state.update_data(ndfl=ndfl)
    await state.update_data(for_author=for_author)

    await state.set_state(GetMoney.get_transfer_data)
    await message.answer(
        f'Введите:\n'
        f' - номер телефона\n'
        f' - имя\n'
        f' - банк\n'
        f'куда необходимо отправить перевод. Если информация будет некорректная заявка будет отклонена')


@router.message(GetMoney.get_transfer_data)
async def withdraw_money(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    if len(message.text) < 10:
        await message.answer(f'Введите как минимум 10 символов')
        return

    await message.answer(f'Заявка отправлена и будет обработана в течении 7 рабочих дней')
    state_data = await state.get_data()
    db.add_money_request(user_id=message.from_user.id, request_data=message.text, commission=state_data["commission"],
                         ndfl=state_data["ndfl"], for_author=state_data["for_author"])
    await state.clear()


@router.message(F.text == 'Выложить запись')
async def create_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    await state.clear()
    await message.answer(
        "Записи распространяются в виде бандлов. \n"
        "Каждый бандл состоит из элементов текста, аудио или фото документов. \n"
        "Необходим добавить как минимум один из элементов. \n"
        "Для того что бы добавить новый элемент просто отправь его новым сообщением.\n"
        "А так же обязательно дождитесь пока все файлы загрузятся, прежде чем идти дальше")

    await message.answer("Для того что бы завершить создание бандла отправье\n/commit")
    await state.set_state(Bundle.assembly)


@router.message(Bundle.assembly)
async def assembly_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    data = await state.get_data()
    list_elements = data.get("assembly", [])

    if message.text == '/commit':
        if len(list_elements) < 1:
            await message.answer("Нужно добавить хотя бы один элемент в бандл")
            return
        await message.answer("Бандл успешно собран")
        await message.answer("Введи название бандла")
        await state.set_state(Bundle.name)
    else:
        if message.content_type is ContentType.TEXT:
            list_elements.append(message.text)
        elif message.content_type is ContentType.DOCUMENT:
            list_elements.append(DocumentMess(message.document.file_id, type_doc="doc", caption=message.caption))
        elif message.content_type is ContentType.AUDIO:
            list_elements.append(DocumentMess(message.audio.file_id, type_doc="audio", caption=message.caption))
        elif message.content_type is ContentType.VIDEO:
            list_elements.append(DocumentMess(message.video.file_id, type_doc="video", caption=message.caption))
        elif message.content_type is ContentType.PHOTO:
            list_elements.append(DocumentMess(message.photo[0].file_id, type_doc="photo", caption=message.caption))
        else:
            await message.answer(
                "Этот формат не поддерживается в бандле. Попробуйте отправить этот документ без сжатия")
        await state.update_data(assembly=list_elements)


@router.message(Bundle.name)
async def name_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    if len(message.text) < 5:
        await message.answer(f'Минимум 5 символов. Сейчас {len(message.text)}')
        return
    if len(message.text) > 40:
        await message.answer(f'Максимум 40 символов. Сейчас {len(message.text)}')
        return
    await state.update_data(name=message.text)

    await message.answer("Введи стоимость в рублях(только число, без доп символов)")
    await state.set_state(Bundle.price)


@router.message(Bundle.price)
async def price_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    try:
        int(message.text)
    except:
        await message.answer("Введите число")
        return

    if int(message.text) == 0 or int(message.text) <= 50:
        await message.answer("Должно быть больше 50")
        return

    await state.update_data(price=message.text)

    await message.answer("Введи название компании(Англ)")
    await state.set_state(Bundle.company)


@router.message(Bundle.company)
async def company_name_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    if len(message.text) < 2:
        await message.answer(f'Минимум 2 символов. Сейчас {len(message.text)}')
        return
    if len(message.text) > 40:
        await message.answer(f'Максимум 40 символов. Сейчас {len(message.text)}')
        return

    await state.update_data(company=message.text)
    await state.set_state(Bundle.date_interview)
    await message.answer("Введи дату собеседования в формате dd.MM.yyyy")


@router.message(Bundle.date_interview)
async def date_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    try:
        time.strptime(message.text, '%d.%m.%Y')
    except:
        await message.answer("Введите дату в правильном формате")
        return

    await state.update_data(date=message.text)
    await state.set_state(Bundle.type)
    await message.answer("Какой тип собеседования? (Скрининг, техническое, знакомство с командой)", reply_markup=kb.type_interview)

@router.message(Bundle.type)
async def date_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    if len(message.text) < 3:
        await message.answer("Введите тип собеседования", reply_markup=kb.type_interview)
        return

    await state.update_data(type=message.text)
    await state.set_state(Bundle.direction)
    await message.answer("Какое направление? BackEnd, FrontEnd и другие", reply_markup=kb.directions)


@router.message(Bundle.direction)
async def grade_bundle(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    await state.update_data(direction=message.text)
    await message.answer(f'Данные записаны и вот так они будут выглядеть для покупателя')
    data = await state.get_data()
    listt = data["assembly"]
    for i in listt:
        if type(i) is DocumentMess:
            if i.type_doc == "doc":
                await message.answer_document(i.file_id, caption=i.caption)
            elif i.type_doc == "audio":
                await message.answer_audio(i.file_id, caption=i.caption)
            elif i.type_doc == "photo":
                await message.answer_photo(i.file_id, caption=i.caption)
            elif i.type_doc == "video":
                await message.answer_video(i.file_id, caption=i.caption)
        else:
            await message.answer(i)
    await message.answer('А в каталоге вакансий будет выглядеть так')
    await message.answer(f'{data["name"]}\n{data["company"]}\n{data["direction"]}\n{data["date"]}\n{data["price"]}₽',
                         reply_markup=kb.create_bundle)


@router.callback_query(F.data == "moderate")
async def callback_query(callback: CallbackQuery, state: FSMContext):
    daoUser.update_last_action(callback.from_user.id)
    if await state.get_state() != str(Bundle.direction.state):
        print("canceled")
        return

    data = await state.get_data()
    await callback.message.answer(
        'Ваш bundle успешно отправлен на модерацию. Когда он пройдет или не пройдет модерацию, вам будет направленно уведомление.',
        reply_markup=kb.main)

    daoBundle.create_bundle(author_id=callback.from_user.id,
                            name=data["name"],
                            price=data["price"],
                            company=data["company"],
                            date_interview=data["date"],
                            direction=data["direction"],
                            assembly=data["assembly"],
                            )
    await state.clear()


@router.callback_query(F.data == "delete")
async def callback_query(callback: CallbackQuery, state: FSMContext):
    daoUser.update_last_action(callback.from_user.id)
    await callback.message.answer("Возвращение в начало чата", reply_markup=kb.main)
    await state.clear()


@router.message(F.text == 'Мои записи')
async def withdraw_money(message: types.Message):
    daoUser.update_last_action(message.from_user.id)
    list_bundles = daoBundle.get_bundles_for_author(message.from_user.id)
    for item in list_bundles:
        await message.answer(
            f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
            f'{item.direction} - {item.company} - {item.date_interview}\n'
            f'скачиваний - {item.bought_count} заработано - {item.earned}₽')
