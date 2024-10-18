from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import config

bot = Bot(token=config.TEST_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))