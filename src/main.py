import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
import logging

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем токен
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Темы
AVAILABLE_TOPICS = {
    "string": "str",
    "числа": "int",
    "дроби": "float",
    "списки": "list",
    "рандом": None
}

# Обработчики

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! 👋\n"
        "Выбери тему или я подберу случайную.",
    )

    keyboard = [[InlineKeyboardButton(topic, callback_data=topic)] for topic in AVAILABLE_TOPICS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери тему:", reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔘 Нажата кнопка!")
    query = update.callback_query
    await query.answer()

    user_answer = query.data
    correct_answer = context.user_data["current_question"]["correct"]

    if user_answer == correct_answer:
        await query.edit_message_text(text=f"✅ Верно!\n\n{context.user_data['current_question']['question']}")
    else:
        hint = context.user_data["current_question"]["hint"]
        await query.edit_message_text(text=f"❌ Неверно.\nПодсказка: {hint}\n\n{context.user_data['current_question']['question']}")


# Главная функция запуска
if __name__ == '__main__':
    print("🚀 Бот стартовал...")

    application = ApplicationBuilder().token(TOKEN).build()

    print("📡 Регистрация обработчиков...")
    application.add_handler(CallbackQueryHandler(handle_answer))  # Сначала обработчики кнопок
    application.add_handler(CommandHandler("start", start))

    print("🔗 Все обработчики зарегистрированы")
    application.run_polling()