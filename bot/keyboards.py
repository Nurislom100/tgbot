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
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "menu_add"), web_app=WebAppInfo(url=webapp_add_url))],
            [KeyboardButton(text=t(lang, "menu_stats"), web_app=WebAppInfo(url=webapp_stats_url))],
        ],
        resize_keyboard=True,
    )
