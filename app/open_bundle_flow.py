import json

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.data.database as db
import app.keyboards as kb
from app.handlers import CatalogFlow
import app.data.BundleDAO as daoBundle
import app.data.UserDAO as daoUser

router = Router()

@router.message(Command('open_bundle'))
async def open_bundle(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Для того что бы открыть напиши id интересующего тебя bundle", protect_content=True)
    await state.set_state(CatalogFlow.choose_id_open)

@router.message(F.text == 'Доступные мне')
async def on_catalog(message: types.Message, state: FSMContext):
    await state.clear()

    list_bundles = daoBundle.get_available_bundles_for_user(user_id=message.from_user.id)

    if len(list_bundles) == 0:
        await message.answer("У вас нет доступных записей. Перейдите в каталог записей для того что бы приобрести еще.", protect_content=True,reply_markup=kb.main)
        return
    await message.answer("Для того что бы открыть напиши /open_bundle", protect_content=True)

    for item in list_bundles:
        await message.answer(
            f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
            f'{item.direction} - {item.company} - {item.date_interview}')


@router.message(CatalogFlow.choose_id_open)
async def date_bundle(message: types.Message, state: FSMContext):
    have_access = daoUser.is_user_have_bundle_access(message.from_user.id, int(message.text))
    if not have_access:
        await message.answer("У вас нет доступа к этому bundle или его не существует. Сначала купите его в разделе \"Каталог интеревью\"")
    else:
        listt = daoBundle.get_bundle_assembling(bundle_id = message.text)
        y: list = json.loads(listt)
        for i in y:
            if type(i) is dict:
                await message.answer_document(i["doc_id"])
            else:
                await message.answer(i)
    await state.clear()