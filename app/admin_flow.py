import json

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import app.data.database as db
from my_bot import bot
import app.data.BundleDAO as daoBundle
import app.data.UserDAO as daoUser

router = Router()

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

    list_bundles = daoBundle.get_not_moderated_bundle()
    await message.answer(f'На модерации - {len(list_bundles)}')

    if len(list_bundles) == 0:
        return

    item = list_bundles[0]
    await message.answer(
        f'(id {item.bundle_id}) - {item.name} - {item.price}₽\n'
        f'{item.direction} - {item.company} - {item.date_interview}')

    await state.set_state(AdminFlow.moderate)
    await state.update_data(bundle=item)
    listt = daoBundle.get_bundle_assembling(bundle_id=item.bundle_id)
    y: list = json.loads(listt)
    for i in y:
        if type(i) is dict:
            if i["type_doc"] == "doc":
                await message.answer_document(i["file_id"], protect_content=True)
            elif i["type_doc"] == "audio":
                await message.answer_audio(i["file_id"], protect_content=True)
            elif i["type_doc"] == "photo":
                await message.answer_photo(i["file_id"], protect_content=True)
            elif i["type_doc"] == "video":
                await message.answer_video(i["file_id"], protect_content=True)
        else:
            await message.answer(i, protect_content=True)

    await message.answer(f'/approve - принять\n'
                         f'/reject - отклонить')


@router.message(Command('approve'))
async def on_admin(message: types.Message, state: FSMContext):
    if await state.get_state() != str(AdminFlow.moderate.state):
        await message.answer(f'Доступ запрещен')
        return
    await message.answer(f'Принято')
    state_data = await state.get_data()
    await daoBundle.approve_bundle(bundle_id=state_data["bundle"].bundle_id)

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

    daoBundle.delete_bundle(bundle_id=state_data["bundle"].bundle_id)

    await state.set_state(AdminFlow.in_admin)
    await moderate_bundle(message, state)
