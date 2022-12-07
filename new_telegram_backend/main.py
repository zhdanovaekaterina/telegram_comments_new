import logging
import asyncio

from back import backend_and_notifications as backend
from front import bot_main as front

# Задаем настройки модуля логгирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    force=True,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
)


def main():
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(backend.backend())
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info('Клиент остановлен.')


if __name__ == '__main__':
    # backend.main()

    asyncio.run(backend.main())

    # asyncio.run(front.bot_func())
