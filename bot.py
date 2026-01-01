import telebot
import requests
import os

# Токен берётся из Secrets на Replit (безопасно!)
BOT_TOKEN = os.getenv("BOT_TOKEN")

if BOT_TOKEN is None:
    print("ОШИБКА: BOT_TOKEN не найден! Добавь в Secrets на Replit.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, 
        "Привет! Я бот для проверки хостинга серверов Minecraft Bedrock.\n\n"
        "Введите /whois <домен или IP> для получения информации."
    )

@bot.message_handler(commands=['whois'])
