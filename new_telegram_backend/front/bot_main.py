from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from new_telegram_backend import config as c
from new_telegram_backend.front import handlers


async def bot_func():
    bot = Bot(token=c.token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers.router)

    print('Start polling')
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
