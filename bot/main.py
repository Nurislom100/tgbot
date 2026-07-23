import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

import database as db
from i18n import INTRO_TEXT, t
from keyboards import language_keyboard, main_menu_keyboard

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_ADD_URL = os.environ["WEBAPP_ADD_URL"]     # masalan https://sizning-domen.com/add.html
WEBAPP_STATS_URL = os.environ["WEBAPP_STATS_URL"] # masalan https://sizning-domen.com/stats.html

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Registration(StatesGroup):
    waiting_name = State()


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    distributor = db.get_distributor(message.from_user.id)
    if distributor:
        lang = distributor["language"]
        await message.answer(
            t(lang, "add_hint"),
            reply_markup=main_menu_keyboard(lang, WEBAPP_ADD_URL, WEBAPP_STATS_URL),
        )
        return

    await message.answer(INTRO_TEXT, reply_markup=language_keyboard())


@dp.callback_query(F.data.startswith("lang:"))
async def on_language_chosen(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":", 1)[1]
    await state.update_data(language=lang)
    await state.set_state(Registration.waiting_name)
    await callback.message.edit_text(t(lang, "ask_name"))
    await callback.answer()


@dp.message(Registration.waiting_name)
async def on_name_entered(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("language", "uz")
    full_name = message.text.strip()

    db.create_distributor(message.from_user.id, full_name, lang)
    await state.clear()

    await message.answer(t(lang, "name_saved", name=full_name))
    await message.answer(
        t(lang, "add_hint"),
        reply_markup=main_menu_keyboard(lang, WEBAPP_ADD_URL, WEBAPP_STATS_URL),
    )


@dp.message(Command("hisobot"))
async def cmd_hisobot(message: Message):
    distributor = db.get_distributor(message.from_user.id)
    lang = distributor["language"] if distributor else "uz"
    await message.answer(
        t(lang, "menu_stats"),
        reply_markup=main_menu_keyboard(lang, WEBAPP_ADD_URL, WEBAPP_STATS_URL),
    )


async def health(request):
    return web.Response(text="Bot ishlab turibdi")


async def run_fake_web_server():
    """Render.com bepul Web Service sifatida tanib, xizmatni o'chirib qo'ymasligi uchun."""
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    db.init_db()
    await run_fake_web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
