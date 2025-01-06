import os
import subprocess
import pyautogui
import webbrowser
import requests
from datetime import datetime
from gtts import gTTS  # Библиотека для преобразования текста в речь
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from pyfiglet import Figlet  # Для ASCII-арта

confirmation_requests = {}

# Команда /start – главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("📝 Открыть Блокнот", callback_data="open_notepad"),
            InlineKeyboardButton("📸 Сделать Скриншот", callback_data="screenshot"),
        ],
        [
            InlineKeyboardButton("🔌 Выключить ПК", callback_data="shutdown"),
            InlineKeyboardButton("🔄 Перезагрузить ПК", callback_data="restart"),
        ],
        [
            InlineKeyboardButton("🔍 Открыть YouTube", callback_data="youtube"),
            InlineKeyboardButton("🕒 Показать Время", callback_data="time"),
        ],
        [
            InlineKeyboardButton("🎮 Запустить Steam", callback_data="launch_steam"),
            InlineKeyboardButton("🚗 Запуск Alt:V", callback_data="launch_altv"),
        ],
        [
            InlineKeyboardButton("🔫 Запустить PUBG", callback_data="launch_pubg"),
            InlineKeyboardButton("🎵 Spotify", callback_data="launch_spotify"),
        ],
        [
            InlineKeyboardButton("🔫 CS2", callback_data="launch_cs2"),
            InlineKeyboardButton("💻 Выполнить CMD", callback_data="run_cmd"),
        ],
        [
            InlineKeyboardButton("🎭 Ввести ASCII-текст", callback_data="ascii"),
            InlineKeyboardButton("😂 Рассказать шутку", callback_data="joke"),
        ],
        [
            InlineKeyboardButton("🎮 Мем", callback_data="meme"),
        ],
        [
            InlineKeyboardButton("🎥 TikTok", callback_data="open_tiktok"),
            InlineKeyboardButton("💬 Discord", callback_data="open_discord"),
        ],
        [
            InlineKeyboardButton("📱 Telegram", callback_data="open_telegram"),
            InlineKeyboardButton("📞 Позвонить мужу", callback_data="call_husband"),
        ],
    ]

    await update.message.reply_text(
        "👋 Добро пожаловать! Выберите действие с кнопок ниже или используйте команды:\n\n"
        "📋 Команды:\n"
        "- /ascii [текст] — Генерация ASCII-арта!\n"
        "- /joke — Случайный анекдот\n"
        "- /meme — Отправить случайный мем\n"
        "- /speak [текст] — Озвучить текст\n"
        "- Открыть TikTok, Discord, Telegram или позвонить мужу из меню.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# Показ времени
async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"🕒 Текущее системное время: `{now}`", parse_mode="Markdown")


# Генерация ASCII-арта
async def ascii_art(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Введите текст для ASCII-арта\nПример: `/ascii hello`")
        return
    text = " ".join(context.args)

    try:
        f = Figlet(font="slant")  # Генерация текста в стиле "slant"
        art = f.renderText(text)
        await update.message.reply_text(f"```\n{art}\n```", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при создании ASCII-арта: {e}")


# Функция для озвучивания текста
async def speak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Введите текст для озвучивания\nПример: `/speak Привет, как дела?`")
        return

    text = " ".join(context.args)
    lang = "ru"

    try:
        # Создаем MP3 файл с использованием gTTS
        tts = gTTS(text=text, lang=lang)
        file_path = "output.mp3"
        tts.save(file_path)

        # Отправляем файл пользователю
        with open(file_path, "rb") as audio:
            await update.message.reply_audio(audio=audio, caption="🎙️ Вот ваша озвучка!")

        # Удаляем файл после отправки
        os.remove(file_path)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при озвучивании текста: {e}")


# Шутки
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "Почему программисты никогда не загорают? Потому что у них слишком много cache.",
        "Что говорит программист перед едой? Ctrl + Alt + Del.",
        "Почему у компьютеров всегда хорошее настроение? Они битами питаются.",
    ]
    random_joke = jokes[datetime.now().second % len(jokes)]  # Берем шутку по времени
    await update.message.reply_text(f"😂 {random_joke}")


# Команда получения мемов
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://www.reddit.com/r/memes.json?limit=100"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        memes = response.json()["data"]["children"]

        meme = memes[datetime.now().second % len(memes)]["data"]["url"]
        await update.message.reply_photo(meme)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении мема: {e}")


# Обработка нажатий кнопок (добавляем speak)
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "ascii":
        await query.message.reply_text("Введите `/ascii [текст]` для ASCII-арта!")
    elif query.data == "joke":
        await joke(query, context)
    elif query.data == "meme":
        await meme(query, context)
    elif query.data == "open_tiktok":
        await open_tiktok(update, context)
    elif query.data == "open_discord":
        await open_discord(update, context)
    elif query.data == "open_telegram":
        await open_telegram(update, context)
    elif query.data == "call_husband":
        await call_husband(update, context)


# Основной запуск бота
def main():
    TOKEN = "Укажите токен вашего бота"  # Укажите токен вашего бота

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("time", get_time))
    app.add_handler(CommandHandler("ascii", ascii_art))
    app.add_handler(CommandHandler("speak", speak))  # Команда для озвучивания текста
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CallbackQueryHandler(handle_callback))  # Все кнопки

    print("🚀 Бот запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()