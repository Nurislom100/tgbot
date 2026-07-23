# Yetkazma boti (dastavshiklar uchun)

## Loyiha tuzilishi
```
tgbot/
  bot/            -> Telegram bot (aiogram)
  backend/        -> API server (FastAPI) - Mini App bilan gaplashadi
  webapp/         -> Mini App sahifalari (add.html, stats.html)
  uploads/        -> saqlangan rasmlar
  data.db         -> SQLite baza (avtomatik yaratiladi)
```

## 1. BotFather'da bot yaratish
1. Telegram'da @BotFather ga yozing, `/newbot` bering, tokenni saqlab qo'ying.
2. `/mybots` -> botingiz -> Bot Settings -> Menu Button -> keyinroq WebApp URL qo'yasiz (ixtiyoriy, chunki menyu tugmalarini bot o'zi yuboradi).

## 2. Yandex Maps API kaliti (ixtiyoriy, lekin xarita uchun kerak)
https://developer.tech.yandex.ru saytidan bepul "JavaScript API va HTTP Geokodlash" kaliti oling.
`webapp/add.html` faylida `YANDEX_API_KEY` so'zini shu kalitga almashtiring.

## 3. Muhit o'zgaruvchilari
`.env` fayl yarating (yoki serverga to'g'ridan-to'g'ri kiriting):
```
BOT_TOKEN=123456:AA...sizning_tokeningiz
WEBAPP_ADD_URL=https://sizning-domen.com/add.html
WEBAPP_STATS_URL=https://sizning-domen.com/stats.html
```
**Muhim**: Telegram Mini App faqat **HTTPS** manzilda ishlaydi. Localhost bilan ishlamaydi.

## 4. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt --break-system-packages
```

## 5. Ishga tushirish (ikkita jarayon kerak)

Backend (webapp'ni ham shu serve qiladi):
```bash
cd backend
BOT_TOKEN=... uvicorn main:app --host 0.0.0.0 --port 8000
```

Bot:
```bash
cd bot
BOT_TOKEN=... WEBAPP_ADD_URL=https://.../add.html WEBAPP_STATS_URL=https://.../stats.html python main.py
```

## 6. Test qilish uchun tezkor usul (ngrok)
Agar hali serveringiz bo'lmasa, mahalliy kompyuterda sinash uchun:
```bash
ngrok http 8000
```
ngrok bergan `https://xxxx.ngrok-free.app` manzilini `WEBAPP_ADD_URL` va `WEBAPP_STATS_URL`ga qo'ying (masalan `.../add.html`).

## 7. Doimiy (production) joylashtirish
Oddiy va bepul variantlardan biri — **Railway.app** yoki **Render.com**:
1. Loyihani GitHub'ga yuklang.
2. Railway/Render'da yangi loyiha oching, GitHub repo'ni ulang.
3. Ikkita xizmat (service) yarating: biri `backend` uchun (uvicorn), biri `bot` uchun (python main.py).
4. Muhit o'zgaruvchilarini (BOT_TOKEN va h.k.) sozlamalarga kiriting.
5. Backend xizmatiga berilgan domenni WEBAPP_ADD_URL/WEBAPP_STATS_URL sifatida bot xizmatiga bering.

## Ma'lumotlar xavfsizligi
Har bir so'rov Telegram'ning `initData` imzosi orqali tekshiriladi (`backend/auth.py`),
shuning uchun dastavshiklar bir-birining ma'lumotini ko'ra olmaydi va soxta so'rov yubora olmaydi.

## /hisobot haqida
Har bir dastavshik botga `/hisobot` yozganda yoki "📊 Statistika" tugmasini bosganda,
faqat **o'zining** oy/yil bo'yicha statistikasini va qaydlarini ko'radi (bu "Mening qaydlarim"
bilan bir sahifada birlashtirilgan — `stats.html`).
