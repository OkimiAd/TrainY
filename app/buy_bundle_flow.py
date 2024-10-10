from aiogram import types, Router, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice, Message
from aiohttp.web_fileresponse import content_type

from app.data.entities import Bundle
from app.handlers import CatalogFlow

import app.keyboards as kb
import app.data.BundleDAO as daoBundle
from config import PAYMENTS_TOKEN
from my_bot import bot

from aiogram.types import PreCheckoutQuery

router = Router()


@router.message(F.text == 'Каталог интервью')
async def on_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Какое направление программирования вас интересует", protect_content=True,
                         reply_markup=kb.directions)
    await state.set_state(CatalogFlow.filter_direction)


@router.message(CatalogFlow.filter_direction)
async def filter_direction(message: types.Message, state: FSMContext):
    await state.update_data(direction=message.text)
    await state.set_state(CatalogFlow.filter_company)
    await message.answer("Какая компания вас интересует?(Англ)", protect_content=True, reply_markup=kb.doesnt_matter)


@router.message(CatalogFlow.filter_company)
async def filter_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await state.set_state(CatalogFlow.filter_company)
    await show_filtered_bundles(message, state)


async def show_filtered_bundles(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    list_bundles = daoBundle.get_filtered_bundles(message.from_user.id, company=state_data["company"],
                                                  direction=state_data["direction"])

    await state.clear()
    if len(list_bundles) == 0:
        await message.answer("К сожалению таких записей пока еще нет", protect_content=True, reply_markup=kb.main)
        return

    await message.answer("Вот список", protect_content=True, reply_markup=kb.main)

    for item in list_bundles:
        await message.answer(
            f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
            f'{item.direction} - {item.company} - {item.date_interview} \n{item.bought_count} раз купили', )
    await message.answer("Для того что бы купить напиши /buy_bundle", protect_content=True)


@router.message(Command('buy_bundle'))
async def buy_bundle(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Напиши id интересующего тебя bundle", protect_content=True)
    await state.set_state(CatalogFlow.choose_id_buy)


@router.message(CatalogFlow.choose_id_buy)
async def date_bundle(message: types.Message, state: FSMContext):
    try:
        int(message.text)
    except:
        await message.answer("Введите id бандла *\(только число\)*", parse_mode=ParseMode.MARKDOWN_V2)
    bundle = daoBundle.get_bundle(bundle_id=int(message.text))

    await state.clear()
    await state.update_data(bundle_id=int(message.text))

    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж")

    await bot.send_invoice(
        message.chat.id,
        title="Покупка пака",
        description=f'(id {bundle.bundle_id}) - {bundle.name} - {bundle.price}₽\n'
                    f'{bundle.direction} - {bundle.company} - {bundle.date_interview}',
        provider_token=PAYMENTS_TOKEN,
        currency='rub',
        photo_url="https://static.sobaka.ru/uploads/nsk/1.jpg",
        photo_height=512,  # !=0/None, иначе изображение не покажется
        photo_width=512,
        photo_size=512,
        is_flexible=False,  # True если конечная цена зависит от способа доставки
        prices=[LabeledPrice(amount=bundle.price * 100, label="Цена")],
        protect_content=True,
        # start_parameter='time-machine-example',
        payload='payload'
    )


@router.message(F.successful_payment)
async def success_payment_handler(message: Message, state: FSMContext):
    await message.answer(text="🥳Спасибо за вашу поддержку!🤗")
    await message.answer(text="Теперь вы можете найти вашу покупку в разделе \"Мои покупки\"")
    state_data = await state.get_data()
    daoBundle.buy_bundle(user_id=message.from_user.id, bundle_id=state_data["bundle_id"])
    await state.clear()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

# @router.pre_checkout_query()
# async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
#     await message.answer("Bundle успешно куплен. Теперь ты его можешь найти в разделе \"Доступные мне\"")
