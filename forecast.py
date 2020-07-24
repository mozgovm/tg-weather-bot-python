from dotenv import load_dotenv
import os
import requests as req

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


class CurrentForecastShort(object):
    def __init__(self, route):
        self.temp = round(route['temp_c'])
        self.cloudness = route['condition']['code']
        self.wind_speed = round(route['wind_kph'] / 3.6, 1)
        self.wind_direction = route['wind_dir']
        self.pressure = round(route['pressure_mb'] * 0.750063755419211)
        self.humidity = route['humidity']
        self.isDay = route['is_day']


class ForecastShort(object):
    def __init__(self, route):
        self.temp = round(route['day']['maxtemp_c'])
        self.cloudness = route['day']['condition']['code']
        self.wind_speed = round(route['day']['maxwind_kph'] / 3.6, 1)
        self.humidity = route['day']['avghumidity']
        self.date = '.'.join(route['date'].split('-')[::-1]) # превращаем дату формата 2020-05-19 в дату формата 19.05.2020


forecast_types = {
    'now': 'сейчас',
    'today': 'сегодня',
    'tomorrow': 'завтра'
}


def parse_forecast(forecast, forecast_type):
    if forecast_type == forecast_types['now']:
        route = forecast['current']
        forecast_short = CurrentForecastShort(route)
        return forecast_short.__dict__
    elif forecast_type == forecast_types['today']:
        route = forecast['forecast']['forecastday'][0]
        forecast_short = ForecastShort(route)
        return forecast_short.__dict__
    elif forecast_type == forecast_types['tomorrow']:
        route = forecast['forecast']['forecastday'][1]
        forecast_short = ForecastShort(route)
        return forecast_short.__dict__


def get_forecast_by_coords(lat, lon, forecast_type):
    url = f'http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={lat},{lon}&days=2'
    res = req.get(url)
    forecast = res.json()
    return parse_forecast(forecast, forecast_type)
