import logging
from aiogram import Bot, Dispatcher
from handlers import user
from middlewares import BanMiddleware
from database import init_bans
import os
from dotenv import load_dotenv
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" ,
    handlers=[
        logging.FileHandler("bot_logs.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")
async def main():
    bot = Bot(token='8225047168:AAHUfxCJ9l1XLSrQtI8yAGTKgPaP4hU78WQ')
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
