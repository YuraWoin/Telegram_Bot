"""
ShablonYuStack — Telegram Business Bot Template
Author: YuraWoin (github.com/YuraWoin)
Original repository: github.com/YuraWoin/telegram_bot
Created: 2026

This code is provided for viewing and personal use only.
Do not redistribute or claim authorship. See LICENSE for terms.
"""
import os
import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()

from aiogram import Bot, Dispatcher
from aiohttp import web
from app.handlers import router
from app.database.models import init_db
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

print(os.getcwd())

TOKEN = os.getenv('API_TOKEN').strip("'").strip('"')

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

db_url = os.getenv('DATABASE_URL', 'НЕ ЗАДАНО → fallback на SQLite!')
...

db_url = os.getenv('DATABASE_URL', 'НЕ ЗАДАНО → fallback на SQLite!')
if '@' in db_url:
    db_url_masked = db_url.split('@')[0].split('://')[0] + '://***@' + db_url.split('@')[1]
else:
    db_url_masked = db_url
print(f"🗄️  DATABASE_URL: {db_url_masked}")


async def health(request):
    return web.Response(text="OK")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"HTTP-сервер запущений на порту {port}")



async def main():
    await init_db()
    dp.include_router(router)
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot off')
