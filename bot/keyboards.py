from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)
from i18n import LANG_NAMES, t


def language_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=name, callback_data=f"lang:{code}")]
        for code, name in LANG_NAMES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(lang: str, webapp_add_url: str, webapp_stats_url: str) -> ReplyKeyboardMarkup:
    # Telegram keshini tozalash uchun URL oxiriga app.html va kesh parametri (?v=99) ulaymiz
    if webapp_add_url.endswith("/"):
        clean_url = webapp_add_url[:-1]
    else:
        clean_url = webapp_add_url

    # Agar domen oxirida app.html bo'lmasa, o'zimiz to'g'ri biriktiramiz
    if not clean_url.endswith("app.html"):
        final_add_url = f"{clean_url}/app.html?v=99"
    else:
        final_add_url = f"{clean_url}?v=99"

    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_add"), web_app=WebAppInfo(url=final_add_url))],
            [KeyboardButton(text=t(lang, "menu_stats"), web_app=WebAppInfo(url=webapp_stats_url))],
        ],
        resize_keyboard=True,
    )
