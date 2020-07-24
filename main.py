from dotenv import load_dotenv
load_dotenv()
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")


import db
from bot import bot
from telebot import types

from geolocation import get_location_name, get_index_of_location, move_location
from forecast import forecast_types, get_forecast_by_coords
from response_renderer import forecast_template
from save_location import save_location
from flask import Flask, request


user_queue = []  # id чатов пользователей, от которых ожидается ввод локации
db.connect()


def ask_forecast_type(message, location_name):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    current_forecast = types.KeyboardButton('Погода сейчас')
    todays_forecast = types.KeyboardButton('Погода сегодня')
    tomorrow_forecast = types.KeyboardButton('Прогноз на завтра')
    change_location = types.KeyboardButton('Изменить локацию')
    markup.add(current_forecast, todays_forecast, tomorrow_forecast, change_location)

    bot.send_message(message.chat.id, f'Выберите период прогноза для локации <b><i>{location_name}</i></b>',
                     parse_mode='HTML', reply_markup=markup)


@bot.message_handler(commands=['start'])
def ask_first_location(message):
    user_queue.append(message.chat.id)
    db_user = db.find_user(message.from_user.username)

    if not db_user:
        new_user = db.create_user(message.from_user.username)

    markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    location_button = types.KeyboardButton('Отправить текущее место', request_location=True)
    markup.add(location_button)
    bot.send_message(message.chat.id,
                     'Напишите название локации, для которой хотите узнать погоду или отправьте текущее местоположение (достутпно только для мобильных устройств)',
                     reply_markup=markup)


@bot.message_handler(regexp=r'Погода сейчас')
def return_current_forecast(message):
    db_user = db.find_user(message.from_user.username)
    location = db_user.lastLocations[0]

    location_name, lat, lon = location['locationName'], location['lat'], location['lon']
    forecast = get_forecast_by_coords(lat, lon, forecast_types['now'])

    bot_response = forecast_template(forecast, forecast_types["now"], location_name)
    bot.send_message(message.chat.id, f'{bot_response}', parse_mode='HTML')


@bot.message_handler(regexp=r'Погода сегодня')
def return_todays_forecast(message):
    db_user = db.find_user(message.from_user.username)
    location = db_user.lastLocations[0]

    location_name, lat, lon = location['locationName'], location['lat'], location['lon']
    forecast = get_forecast_by_coords(lat, lon, forecast_types['today'])

    bot_response = forecast_template(forecast, forecast_types["today"], location_name)
    bot.send_message(message.chat.id, f'{bot_response}', parse_mode='HTML')


@bot.message_handler(regexp=r'Прогноз на завтра')
def return_tomorrow_forecast(message):
    db_user = db.find_user(message.from_user.username)
    location = db_user.lastLocations[0]

    location_name, lat, lon = location['locationName'], location['lat'], location['lon']
    forecast = get_forecast_by_coords(lat, lon, forecast_types['tomorrow'])

    bot_response = forecast_template(forecast, forecast_types["tomorrow"], location_name)
    bot.send_message(message.chat.id, f'{bot_response}', parse_mode='HTML')


@bot.message_handler(regexp=r'Изменить локацию')
def change_location(message):
    user_queue.append(message.chat.id)

    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    location_button = types.KeyboardButton('Отправить текущее место', request_location=True)
    cancel_button = types.KeyboardButton('Отмена')
    markup.add(location_button, cancel_button)
    bot.send_message(message.chat.id,
                     'Напишите название локации, для которой хотите узнать погоду или отправьте текущее местоположение (достутпно только для мобильных устройств)',
                     reply_markup=markup)


@bot.message_handler(regexp=r'Отмена')
def cancel_change_location(message):
    db_user = db.find_user(message.from_user.username)
    location = db_user.lastLocations[0]

    chat_index = user_queue.index(message.chat.id)
    del user_queue[chat_index]

    ask_forecast_type(message, location['locationName'])


@bot.message_handler(content_types=['location'])
def save_current_location(message):
    latitude, longitude = message.location.latitude, message.location.longitude

    current_location = get_location_name(latitude, longitude)

    db_user = db.find_user(message.from_user.username)

    if not db_user.lastLocations:
        db_user.lastLocations.append({
            'locationName': current_location,
            'lat': latitude,
            'lon': longitude
        })
    else:
        location_index = get_index_of_location(db_user.lastLocations, current_location)

        if location_index == -1:
            db_user.lastLocations.insert(0, {
                'locationName': current_location,
                'lat': latitude,
                'lon': longitude
            })
        else:
            move_location(db_user.lastLocations, location_index)

    while len(db_user.lastLocations) > 3:
        del db_user.lastLocations[-1]

    db_user.save()

    chat_index = user_queue.index(message.chat.id)
    del user_queue[chat_index]

    ask_forecast_type(message, current_location)


@bot.message_handler()
def reply_for_location(message):
    waiting_for_location_from_user = message.chat.id in user_queue
    location_change_cancelled = message.text == 'Отмена'
    location_received_by_gps = message.location

    if waiting_for_location_from_user and not location_change_cancelled and not location_received_by_gps:
        location_name = save_location(message)

        if not location_name:
            return

        chat_index = user_queue.index(message.chat.id)
        del user_queue[chat_index]

        ask_forecast_type(message, location_name)


# bot.polling()
app = Flask(__name__)


@app.route(f'/weather_bot{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200
