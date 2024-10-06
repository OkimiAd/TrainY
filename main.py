import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import app.database
import config
from app.buy_bundle_flow import router as buy_bundle_flow
from app.create_bundle_flow import router as create_bl_router
from app.handlers import router as handler_router


async def main():
    bot = Bot(token=config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await app.database.db_start()

    dp.include_routers(create_bl_router, buy_bundle_flow, handler_router)
    await dp.start_polling(bot)
    print("start_polling")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
