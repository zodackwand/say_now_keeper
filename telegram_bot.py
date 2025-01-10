import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from text_recognizer import recognize_speech_from_file
from GPT_controller import get_response
import sqlite3
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Вставьте ваш токен бота
TOKEN = os.environ.get("TOKEN")

# Функция для обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Отправь мне голосовое сообщение, и я его сохраню.')

def add_purchase(purchase_type, amount_spent, currency, telegram_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchases (date, purchase_type, amount_spent, currency, telegram_id)
        VALUES (CURRENT_DATE, ?, ?, ?, ?)
    ''', (purchase_type, amount_spent, currency, telegram_id))
    conn.commit()
    conn.close()

# Функция для обработки голосовых сообщений
async def voice_handler(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = f'voice_{voice.file_id}.wav'
    await file.download_to_drive(file_path)
    #await update.message.reply_text(f'Голосовое сообщение сохранено как {file_path}')
    await update.message.reply_text(f'Обработка голосового сообщения...') 

    # Распознаем речь
    recognized_text = recognize_speech_from_file(file_path)
    await update.message.reply_text(f'Распознанный текст: {recognized_text}')

    # Получаем ответ от GPT
    gpt_response = get_response(recognized_text)
    #await update.message.reply_text(f'Ответ GPT: {gpt_response}')

    # Добавляем покупку в базу данных
    telegram_id = update.message.from_user.id
    add_purchase(gpt_response["purchase_type"], gpt_response["amount spent"], gpt_response["currency in standard form of the word"], telegram_id)

    # Удаляем звуковой файл после обработки
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            print(f"Файл {file_path} успешно удален.")
        except Exception as e:
            print(f"Ошибка при удалении файла {file_path}: {e}")
    else:
        print(f"Файл {file_path} не найден.")

# Форматируем сообщение о сохранении данных
    saved_message = (
        f"Данные были сохранены:\n"
        f"Тип покупки: {gpt_response['purchase_type']}\n"
        f"Сумма: {gpt_response['amount spent']}\n"
        f"Валюта: {gpt_response['currency in standard form of the word']}"
    )

    # Отправляем сообщение пользователю
    await update.message.reply_text(saved_message)

def main() -> None:
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()