import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from text_recognizer import recognize_speech_from_file
from GPT_controller import get_response
import sqlite3
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Вставьте ваш токен бота
TOKEN = os.environ.get("TOKEN")

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [[KeyboardButton("/delete_last")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text('Привет! Отправь мне голосовое сообщение, и я его сохраню.', reply_markup=reply_markup)

def add_purchase(purchase_type, amount_spent, currency, telegram_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO purchases (date, purchase_type, amount_spent, currency, telegram_id)
        VALUES (CURRENT_DATE, ?, ?, ?, ?)
    ''', (purchase_type, amount_spent, currency, telegram_id))
    conn.commit()
    conn.close()

def delete_last_purchase(telegram_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Выбираем последнюю запись для данного telegram_id
    cursor.execute('''
        SELECT id, purchase_type, amount_spent
        FROM purchases
        WHERE telegram_id = ?
        ORDER BY date DESC, id DESC
        LIMIT 1
    ''', (telegram_id,))
    last_purchase = cursor.fetchone()

    if last_purchase:
        purchase_id, purchase_type, amount_spent = last_purchase

        # Удаляем последнюю запись
        cursor.execute('''
            DELETE FROM purchases
            WHERE id = ?
        ''', (purchase_id,))
        conn.commit()
        conn.close()

        return purchase_type, amount_spent
    else:
        conn.close()
        return None, None

# Функция для обработки голосовых сообщений
async def voice_handler(update: Update, context: CallbackContext) -> None:
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = f'voice_{voice.file_id}.wav'
    await file.download_to_drive(file_path)
    await update.message.reply_text(f'Обработка голосового сообщения...') 

    # Распознаем речь
    recognized_text = recognize_speech_from_file(file_path)
    await update.message.reply_text(f'Распознанный текст: {recognized_text}')

    # Получаем ответ от GPT
    gpt_response = get_response(recognized_text)

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

# Функция для обработки команды /delete_last
async def delete_last(update: Update, context: CallbackContext) -> None:
    telegram_id = update.message.from_user.id
    purchase_type, amount_spent = delete_last_purchase(telegram_id)
    
    if purchase_type and amount_spent:
        await update.message.reply_text(f'Последняя запись была удалена.\nКатегория: {purchase_type}\nСумма: {amount_spent}')
    else:
        await update.message.reply_text('Нет записей для удаления.')

def main() -> None:
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("delete_last", delete_last))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))

    # Запускаем бота
    print("Бот запущен.")
    application.run_polling()

if __name__ == '__main__':
    main()