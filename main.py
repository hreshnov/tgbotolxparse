import asyncio
import logging

from config.loader import dp, bot

# [IMPORT ALL HANDLERS]
from bot.handlers.user import welcome, callbacks

# [IMPORT TOKEN]
from logging import basicConfig

# [IMPORT DATABASE MODELS]
from bot.database.models import *

# [IMPORT ADMIN PANEL]
from bot.handlers.admin import edit_menu

# [IMPORT PARSE FUNC]
from bot.olx_parse import olx_parse, BASE_URL
from bot.otodom_parse import otodom_parse, BASE_URLOTD


async def main():

    dp.include_routers(
        welcome.router,
        callbacks.router,
        edit_menu.admin,
    )

    asyncio.create_task(olx_parse(BASE_URL))
    asyncio.create_task(otodom_parse(BASE_URLOTD))
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')