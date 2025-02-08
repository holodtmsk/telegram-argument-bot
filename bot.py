import os
import json
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils import executor
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Храним очки пользователей
user_scores = {}

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

### 🏆 ФУНКЦИЯ АНАЛИЗА ЧЕРЕЗ DEEPSEEK ###
def analyze_with_deepseek(text):
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": "Ты судья в споре. Ответь, кто прав."},
                     {"role": "user", "content": text}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return "Ошибка в DeepSeek API"

### 👀 КОМАНДА /who ДЛЯ СУДА В ЧАТЕ ###
@dp.message_handler(commands=['who'])
async def who_is_right(message: Message):
    # Берём последние 10 сообщений чата
    chat_messages = await message.chat.get_messages(message.message_id - 10, message.message_id)

    # Собираем текст всех сообщений
    text = "\n".join([f"{msg.from_user.full_name}: {msg.text}" for msg in chat_messages if msg.text])

    # Отправляем в DeepSeek API
    verdict = analyze_with_deepseek(text)

    # Найдём имя пользователя, который прав
    winner = None
    for user in message.chat.get_administrators():
        if user.user.full_name in verdict:
            winner = user.user.full_name
            break

    if winner:
        user_scores[winner] = user_scores.get(winner, 0) + 1
        await message.reply(f"🏆 {winner} ПРАВ! Очки: {user_scores[winner]}")
    else:
        await message.reply("🤷‍♂️ DeepSeek не смог определить победителя.")

### 📊 КОМАНДА /scores ДЛЯ ПОКАЗА ОЧКОВ ###
@dp.message_handler(commands=['scores'])
async def show_scores(message: Message):
    if user_scores:
        scores_text = "\n".join([f"{user}: {score} очков" for user, score in user_scores.items()])
        await message.reply(f"🏆 Рейтинг участников:\n{scores_text}")
    else:
        await message.reply("🔹 Пока нет начисленных очков.")

### 🔥 ЗАПУСК БОТА ###
if __name__ == '__main__':
    print("Бот запущен!")
    executor.start_polling(dp, skip_updates=True)
