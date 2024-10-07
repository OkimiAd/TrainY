import asyncio
import logging
import sys

from aiogram import Dispatcher

import app.database
from app.buy_bundle_flow import router as buy_bundle_flow
from app.create_bundle_flow import router as create_bl_router
from app.open_bundle_flow import router as open_bl_router
from app.handlers import router as handler_router
from my_bot import bot


async def main():
    dp = Dispatcher()

    await app.database.db_start()

    dp.include_routers(create_bl_router, buy_bundle_flow,open_bl_router, handler_router)
    await dp.start_polling(bot)
    print("start_polling")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
