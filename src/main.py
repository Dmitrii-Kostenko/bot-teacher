# src/main.py

import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import bot_handlers

# Логирование ошибок
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")


# Обработчик /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! 👋\n"
        "Нажми '🔄 Случайный вопрос', чтобы начать.",
    )

    keyboard = [[InlineKeyboardButton("🔄 Случайный вопрос", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбирай!", reply_markup=reply_markup)


# Получаем случайный вопрос
async def handle_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    question = bot_handlers.get_question(context.bot_data["questions"])
    context.user_data["current_question"] = question

    buttons = [[InlineKeyboardButton(option, callback_data=option)] for option in question["options"]]
    reply_markup = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(text=f"🧠 Вопрос: {question['question']}")
    await query.message.reply_text("Выбери правильный вариант:", reply_markup=reply_markup)


# Проверяем ответ
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_q = context.user_data.get("current_question")
    user_answer = query.data

    if not current_q:
        await query.edit_message_text("❌ Нет активного вопроса")
        return

    correct = current_q["correct"]
    hint = current_q["hint"]

    if user_answer == correct:
        await query.edit_message_text("✅ Верно!")
    else:
        await query.edit_message_text(f"❌ Неверно.\nПодсказка: {hint}")

    # Кнопка следующего вопроса
    next_btn = [[InlineKeyboardButton("🔄 Следующий", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(next_btn)
    await query.message.reply_text("Нажми ниже:", reply_markup=reply_markup)


# Главная точка входа
if __name__ == '__main__':
    print("🚀 Бот стартовал...")

    try:
        application = ApplicationBuilder().token(TOKEN).build()
        application.bot_data["questions"] = bot_handlers.load_questions()
        print("📚 Вопросы загружены")
    except Exception as e:
        print("❌ Ошибка загрузки вопросов:", str(e))
        exit()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_random, pattern="^random$"))
    application.add_handler(CallbackQueryHandler(handle_answer))

    # Обработчик ошибок
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        logger.warning('⚠️ Произошла ошибка: %s', context.error)

    application.add_error_handler(error_handler)

    print("📡 Бот запущен...")
    application.run_polling()