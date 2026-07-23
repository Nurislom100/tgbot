TEXTS = {
    "uz": {
        "ask_name": "Ismingizni kiriting (masalan: Aziz Karimov):",
        "name_saved": "Rahmat, {name}! Endi tayyorsiz.",
        "menu_add": "➕ Qayd qo'shish",
        "menu_stats": "📊 Statistika / Mening qaydlarim",
        "add_hint": "Yangi yetkazma qo'shish uchun tugmani bosing.",
        "saved_ok": "✅ Qayd saqlandi. Yana qo'shishingiz mumkin.",
    },
    "ru": {
        "ask_name": "Введите ваше имя (например: Азиз Каримов):",
        "name_saved": "Спасибо, {name}! Теперь всё готово.",
        "menu_add": "➕ Добавить запись",
        "menu_stats": "📊 Статистика / Мои записи",
        "add_hint": "Нажмите кнопку, чтобы добавить новую доставку.",
        "saved_ok": "✅ Запись сохранена. Можете добавить ещё.",
    },
    "en": {
        "ask_name": "Enter your name (e.g. Aziz Karimov):",
        "name_saved": "Thanks, {name}! You're all set.",
        "menu_add": "➕ Add record",
        "menu_stats": "📊 Statistics / My records",
        "add_hint": "Tap the button to add a new delivery.",
        "saved_ok": "✅ Record saved. You can add more.",
    },
}

INTRO_TEXT = (
    "🇺🇿 <b>Yetkazma botiga xush kelibsiz!</b>\n"
    "Bu bot dastavshiklar do'konlarga qachon, qaysi mahsulotni yetkazganini "
    "qayd qilib borishi uchun yaratilgan.\n\n"
    "🇷🇺 <b>Добро пожаловать в бот доставки!</b>\n"
    "Этот бот создан для того, чтобы доставщики фиксировали, когда и какой "
    "товар они доставили в магазины."
)

LANG_NAMES = {"uz": "O'zbek", "ru": "Русский", "en": "English"}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in TEXTS else "uz"
    text = TEXTS[lang].get(key, TEXTS["uz"].get(key, key))
    return text.format(**kwargs) if kwargs else text
