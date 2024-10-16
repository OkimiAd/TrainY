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
    moderate_bundle = State()
    moderate_request_money = State()
    reject_bundle = State()
    reject_money_request = State()


@router.message(Command('admin'))
async def on_admin(message: types.Message, state: FSMContext):
    daoUser.update_last_action(message.from_user.id)
    await state.set_state(AdminFlow.password)
    user = daoUser.get_user(user_id=message.from_user.id)
    if user.job_title == "Admin":
        await message.answer("Вы успешно вошли в админку")

        list_bundles = daoBundle.get_not_moderated_bundle()
        list_money_requests = db.get_active_money_requests()

        await message.answer(f'/moderate_bundle - для того что бы увидеть ожидающий бандл - {len(list_bundles)}\n'
                             f'/money_requests -  для того что бы увидеть заявки на вывод средств - {len(list_money_requests)}')
        await state.set_state(AdminFlow.in_admin)
    else:
        await message.answer("Нет доступа")

@router.message(Command('money_requests'))
async def money_requests(message: types.Message, state: FSMContext):
    if await state.get_state() != str(AdminFlow.in_admin.state):
        await message.answer(f'Доступ запрещен')
        return

    list_money_requests = db.get_active_money_requests()
    await message.answer(f'На рассмотрении - {len(list_money_requests)}')

    if len(list_money_requests) == 0:
        return
    item = list_money_requests[0]

    await state.update_data(money_requests=item)

    await message.answer(
        f'{item.created_date}\nавтору - {item.for_author}₽, коммиссия - {item.commission}₽, НДФЛ - {item.ndfl}₽\n{item.request_date}',
        protect_content=True)

    await message.answer(f'/approve - принять\n'
                         f'/reject - отклонить')
    await state.set_state(AdminFlow.moderate_request_money)


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

    await state.set_state(AdminFlow.moderate_bundle)
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
    if await state.get_state() == str(AdminFlow.moderate_bundle.state):
        await message.answer(f'Принято')
        state_data = await state.get_data()
        await daoBundle.approve_bundle(bundle_id=state_data["bundle"].bundle_id)

        await bot.send_message(chat_id=state_data["bundle"].author_id,
                               text=f'Ваш Bundle id - {state_data["bundle"].bundle_id} был принят')

        await state.set_state(AdminFlow.in_admin)
        await moderate_bundle(message, state)
    elif await state.get_state() == str(AdminFlow.moderate_request_money.state):
        await message.answer(f'Принято')

        state_data = await state.get_data()

        total = state_data["money_requests"].for_author + state_data["money_requests"].commission + state_data[
            "money_requests"].ndfl

        await bot.send_message(chat_id=state_data["money_requests"].user_id,
                               text=f'Ваш запрос на вывод денег id - {state_data["money_requests"].id} был принят.\n{state_data["money_requests"].for_author}₽')
        db.set_money_request_status(mr_id=state_data["money_requests"].id, status=2)
        daoUser.credit_to_the_user(user_id=state_data["money_requests"].user_id,
                                   cash=-total)
        await state.set_state(AdminFlow.in_admin)
        await money_requests(message, state)
    else:
        await message.answer(f'Доступ запрещен')
        return


@router.message(Command('reject'))
async def on_admin(message: types.Message, state: FSMContext):
    if await state.get_state() == str(AdminFlow.moderate_bundle.state):
        await message.answer(f'Напишите причину отказа')
        await state.set_state(AdminFlow.reject_bundle)
    elif await state.get_state() == str(AdminFlow.moderate_request_money.state):
        await message.answer(f'Напишите причину отказа')
        await state.set_state(AdminFlow.reject_money_request)
    else:
        await message.answer(f'Доступ запрещен')
        return


@router.message(AdminFlow.reject_bundle)
async def on_admin(message: types.Message, state: FSMContext):
    await message.answer(f'Отклонено')
    state_data = await state.get_data()
    await bot.send_message(chat_id=state_data["bundle"].author_id,
                           text=f'Ваш Bundle id - {state_data["bundle"].bundle_id} был отклонен')

    await bot.send_message(chat_id=state_data["bundle"].author_id,
                           text=f'Причина - {message.text}')

    daoBundle.delete_bundle(bundle_id=state_data["bundle"].bundle_id)

    await state.set_state(AdminFlow.in_admin)
    await moderate_bundle(message, state)


@router.message(AdminFlow.reject_money_request)
async def on_admin(message: types.Message, state: FSMContext):
    await message.answer(f'Отклонено')
    state_data = await state.get_data()
    await bot.send_message(chat_id=state_data["money_requests"].user_id,
                           text=f'Ваш запрос на вывод денег id - {state_data["money_requests"].id} был отклонен.\n'
                                f'Заяка создана {state_data["money_requests"].created_date}\n'
                                f'{state_data["money_requests"].for_author + state_data["money_requests"].commission + state_data["money_requests"].ndfl}₽\n'
                                f'{state_data["money_requests"].request_date}')

    await bot.send_message(chat_id=state_data["money_requests"].user_id,
                           text=f'Причина - {message.text}')

    db.set_money_request_status(mr_id=state_data["money_requests"].id, status=1)

    await state.set_state(AdminFlow.in_admin)
    await money_requests(message, state)
