import logging

from aiogram import (
    Bot,
    Dispatcher,
)

from technesis.constants import BOT_TOKEN
from technesis.handlers import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("technesis_logger")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)
