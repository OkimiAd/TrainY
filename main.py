import asyncio
import logging
import sys

from aiogram import Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

import app.data.database
from aiogram import types
from app.buy_bundle_flow import router as buy_bundle_flow
from app.create_bundle_flow import router as create_bl_router
from app.open_bundle_flow import router as open_bl_router
from app.admin_flow import router as admin_router
from app.handlers import router as handler_router
from my_bot import bot
import app.keyboards as kb
import app.data.database as db
import app.data.BundleDAO as daoBundle
import app.data.UserDAO as daoUser

dp = Dispatcher()


@dp.message(CommandStart())
async def on_start(message: types.Message, state: FSMContext):
    user = message.from_user
    await message.answer_sticker("CAACAgIAAxkBAAEM6o9m_xXrhAqbSSVi3qlJF-avCUEN0AACSB0AAuIkgEot-Nk2wyVajjYE")
    await message.answer("Привет " + user.first_name)
    await message.answer(
        "Это бот TrainY! Тут ты можешь найти свежие записи собеседований в любую компанию на любую должность.\n"
        "Для начала можешь перейти в каталог интервью.☺️",
        reply_markup=kb.main)


    daoUser.add_user(user.id, user.username)
    await state.clear()


@dp.message(Command('cancel'))
async def on_cancel(message: types.Message, state: FSMContext):
    await message.answer("Возвращение в начало чата")
    await state.clear()


async def main():
    app.data.database.db_start()

    dp.include_routers(create_bl_router, buy_bundle_flow, open_bl_router, admin_router, handler_router)
    await dp.start_polling(bot)
    print("start_polling")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
