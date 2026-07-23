import asyncio
import json
import logging
import os
import threading
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer

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


# =========================================================
# WEB APP'DAN KELGAN MA'LUMOTLARNI QABUL QILUVCHI HANDLER
# =========================================================
@dp.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    try:
        # WebApp jo'natgan JSON matnni o'qiymiz
        raw_data = message.web_app_data.data
        data = json.loads(raw_data)

        user_id = message.from_user.id
        distributor = db.get_distributor(user_id)
        lang = distributor["language"] if distributor else "uz"

        shop_name = data.get("shop_name")
        address_text = data.get("address_text")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        phone = data.get("phone")
        product_name = data.get("product_name")
        quantity = data.get("quantity")
        photo_base64 = data.get("photo_base64")

        # Database (baza) ga saqlash
        # database.py faylingizdagi funksiya nomiga moslab tekshirib oling:
        if hasattr(db, "add_record"):
            db.add_record(
                distributor_id=user_id,
                shop_name=shop_name,
                address_text=address_text,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                product_name=product_name,
                quantity=quantity,
                photo_base64=photo_base64
            )
        elif hasattr(db, "create_record"):
            db.create_record(
                distributor_id=user_id,
                shop_name=shop_name,
                address_text=address_text,
                latitude=latitude,
                longitude=longitude,
                phone=phone,
                product_name=product_name,
                quantity=quantity,
                photo_base64=photo_base64
            )

        # Foydalanuvchiga muvaffaqiyatli saqlangani haqida bildirishnoma yuborish
        msg_text = f"✅ **Qayd saqlandi!**\n\n" \
                   f"🏪 **Do'kon:** {shop_name}\n"
        
        if address_text:
            msg_text += f"📍 **Manzil:** {address_text}\n"
        if product_name:
            msg_text += f"📦 **Mahsulot:** {product_name}\n"
        if quantity:
            msg_text += f"🔢 **Miqdori:** {quantity}\n"

        await message.answer(msg_text, parse_mode="Markdown")

        # Agar joylashuv (koordinata) bo'lsa, xarita yuborish
        if latitude and longitude:
            await message.answer_location(latitude=float(latitude), longitude=float(longitude))

    except Exception as e:
        logging.error(f"WebApp ma'lumotlarini saqlashda xatolik: {e}")
        await message.answer("❌ Qaydni saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.")


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot ishlab turibdi")

    def log_message(self, format, *args):
        pass  # konsolni chalg'itmaslik uchun


def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()


async def main():
    db.init_db()
    start_health_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
