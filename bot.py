from dotenv import load_dotenv
load_dotenv()
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")

import telebot

bot = telebot.TeleBot(BOT_TOKEN)

