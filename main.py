import misc
import config
import handlers
import asyncio
import logging
import utils

from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
import pytz


# import config


async def main():

    await misc.bot.delete_webhook(drop_pending_updates=True)
    await misc.dp.start_polling(misc.bot, allowed_updates=misc.dp.resolve_used_update_types())


if __name__ == "__main__":
    # import os
 
    # file_db = '/data/bot.db'
    # if os.path.exists(file_db):
    #     os.remove(file_db)

    logging.basicConfig(level=logging.INFO)
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
    # scheduler.add_job(utils.good_morning_all, 'cron', minute=0)
    scheduler.add_job(utils.good_morning_all, 'cron', hour=8)
    scheduler.start()
    asyncio.get_event_loop().run_until_complete(main())
    # asyncio.run(main())
