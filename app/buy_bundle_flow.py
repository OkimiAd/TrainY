
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import app.database as db
from app.handlers import CatalogFlow

router = Router()

@router.message(F.text == 'Каталог интервью')
async def on_catalog(message: types.Message, state: FSMContext):
    await state.clear()
    list_bundles = db.get_all_bundles(message.from_user.id)
    await message.answer("Для того что бы купить напиши /buy_bundle", protect_content=True)

    await state.set_state(CatalogFlow.choose_id_buy)

    for item in list_bundles:
        await message.answer(
            f'id - {item.bundle_id}\n{item.name}\n{item.company}\n{item.direction}\n{item.date_interview}\n{item.price}₽')


@router.message(Command('buy_bundle'))
async def buy_bundle(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Для того что бы купить напиши id интересующего тебя bundle", protect_content=True)
    await state.set_state(CatalogFlow.choose_id_buy)


@router.message(CatalogFlow.choose_id_buy)
async def date_bundle(message: types.Message, state: FSMContext):
    db.add_bundle_for_user(user_id=message.from_user.id, bundle_id=int(message.text))
    await state.clear()
    await message.answer("Bundle успешно куплен. Теперь ты его можешь найти в разделе \"Доступные мне\"")