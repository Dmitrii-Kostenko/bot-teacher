import os
from dotenv import load_dotenv

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! 👋"
        "Я бот для повторения тем. Выбери тему или я подберу случайную.",
    )

    # Создаём кнопку
    button = KeyboardButton("Выбрать тему")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)

    await update.message.reply_text("Нажми кнопку ниже:", reply_markup=reply_markup)


# Точка входа
if __name__ == '__main__':
    print("Бот запущен...")

    # Создаём приложение
    application = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем команду /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()
