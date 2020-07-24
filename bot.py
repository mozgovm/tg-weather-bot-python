from dotenv import load_dotenv
load_dotenv()
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

import telebot

bot = telebot.TeleBot(BOT_TOKEN)

url = f'https://mmozgov-python-weather-bot.herokuapp.com/weather_bot{BOT_TOKEN}'
bot.remove_webhook()
bot.set_webhook(url=url)
