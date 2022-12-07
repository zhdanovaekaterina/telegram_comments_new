import logging
import asyncio
from pathlib import Path
from datetime import datetime

import schedule
import aioschedule
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

import new_telegram_backend.config as c
from new_telegram_backend.front import bot_main as front


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    force=True,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
)


async def backend():
    tg_client = TelegramClient(StringSession(c.session), c.api_id, c.api_hash)

    while True:
        async with tg_client:
            message = datetime.now().strftime("%H:%M:%S")
            await tg_client.send_message(entity=218229736, message=f'Отправка сообщения из клиента {message}')

        logger.info(f'Отправка сообщения из клиента {message}')
        await asyncio.sleep(5)


def main():
    try:
        loop = asyncio.get_event_loop()

        loop.create_task(backend())
        loop.create_task(front.bot_func())

        loop.run_forever()

    except KeyboardInterrupt:
        logger.info('Клиент остановлен.')


# async def some_dull_work():
#     print('Doing some stuff...')
#
#
# async def async_scheduler():
#     aioschedule.every(5).seconds.do(some_dull_work)
#     while True:
#         await aioschedule.run_pending()
#         await asyncio.sleep(2)
#
#
# def sync_scheduler():
#     schedule.every(5).seconds.do(main)
#     while True:
#         schedule.run_pending()

