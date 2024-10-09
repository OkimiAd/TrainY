from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.handlers import CatalogFlow

import app.keyboards as kb
import app.data.BundleDAO as daoBundle

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
        await message.answer("К сожалению таких записей пока еще нет", protect_content=True,reply_markup=kb.main)
        return

    await message.answer("Вот список", protect_content=True,reply_markup=kb.main)

    for item in list_bundles:
        await message.answer(
            f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
            f'{item.direction} - {item.company} - {item.date_interview} \n{item.bought_count} раз купили',)
    await message.answer("Для того что бы купить напиши /buy_bundle", protect_content=True)


@router.message(Command('buy_bundle'))
async def buy_bundle(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Напиши id интересующего тебя bundle", protect_content=True)
    await state.set_state(CatalogFlow.choose_id_buy)


@router.message(CatalogFlow.choose_id_buy)
async def date_bundle(message: types.Message, state: FSMContext):
    daoBundle.buy_bundle(user_id=message.from_user.id, bundle_id=int(message.text))
    await state.clear()
    await message.answer("Bundle успешно куплен. Теперь ты его можешь найти в разделе \"Доступные мне\"")
