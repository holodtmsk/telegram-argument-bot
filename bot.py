import os
import json
import telebot
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Инициализируем Telegram бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Функция запроса к DeepSeek API
def ask_deepseek(question):
    url = "https://deepseek-r1.p.rapidapi.com/"
    headers = {
        "x-rapidapi-key": DEEPSEEK_API_KEY,
        "x-rapidapi-host": "deepseek-r1.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-r1",
        "messages": [{"role": "user", "content": question}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return "Ошибка при обращении к DeepSeek API"

# Обработчик команды /who
@bot.message_handler(commands=["who"])
def handle_who(message):
    question = "Кто прав в этом споре? Проанализируй предыдущие сообщения и выбери сторону."
    response = ask_deepseek(question)
    bot.reply_to(message, response)

# Обработчик всех сообщений
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.reply_to(message, "Привет! Используй команду /who, чтобы узнать, кто прав.")

# Запуск бота
bot.polling()
