import logging
from aiogram import Bot, Dispatcher
from handlers import user
from middlewares import BanMiddleware
from database import init_bans
from config import BOT_TOKEN
from handlers import user
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" ,
    handlers=[
        logging.FileHandler("bot_logs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(user)
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())
    init_bans()
    await dp.start_polling(bot)



if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
