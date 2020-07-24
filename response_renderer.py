from config.wind_directions import wind_directions as wd
import helpers.cloudness as cloudness
from forecast import forecast_types
from textwrap import dedent

cloudness_codes = cloudness.create_cloudness_object(cloudness.get_cloudness_codes(), cloudness.supported_languages)


def get_day_part(isDay):
    return 'day' if isDay == 1 else 'night'


def get_cloudness(code, lang, daypart):
    return cloudness_codes[code][lang][f'{daypart}_text']


def render_cloudness(forecast):
    key = 'isDay'
    if key in forecast:
        return f'<b>{get_cloudness(forecast["cloudness"], "Russian", get_day_part(forecast["isDay"]))}</b>'
    else:
        return f'<b>{get_cloudness(forecast["cloudness"], "Russian", get_day_part(1))}</b>'


def render_plus(temp):
    return '+' if temp > 0 else ''


def get_wind_direction(wind_dir):
    if wind_dir == 'N':
        return f'{wd["north"]["point"]} {wd["north"]["arrow"]}'
    elif wind_dir == 'S':
        return f'{wd["south"]["point"]} {wd["south"]["arrow"]}'
    elif wind_dir == 'W':
        return f'{wd["west"]["point"]} {wd["west"]["arrow"]}'
    elif wind_dir == 'E':
        return f'{wd["east"]["point"]} {wd["east"]["arrow"]}'
    elif wind_dir in ('NW', 'NNW', 'WNW'):
         return f'{wd["north_west"]["point"]} {wd["north_west"]["arrow"]}'
    elif wind_dir in ('NE', 'NNE', 'ENE'):
         return f'{wd["north_east"]["point"]} {wd["north_east"]["arrow"]}'
    elif wind_dir in ('SW', 'SSW', 'WSW'):
         return f'{wd["south_west"]["point"]} {wd["south_west"]["arrow"]}'
    elif wind_dir in ('SE', 'SSE', 'ESE'):
         return f'{wd["south_east"]["point"]} {wd["south_east"]["arrow"]}'


def get_wind_speed(wind_speed, wind_dir = ''):
    if not wind_dir:
        return 'Штиль' if wind_speed == 0 else f'{wind_speed} м/с'
    return 'Штиль' if wind_speed == 0 else f'{wind_speed} м/с, {wind_dir}'


def render_temp(forecast):
    return f'<b>{render_plus(forecast["temp"])}{forecast["temp"]} °C</b>'


def render_wind(forecast):
    key = 'wind_direction'
    if key in forecast:
        return f'<b>{get_wind_speed(forecast["wind_speed"], get_wind_direction(forecast["wind_direction"]))}</b>'
    else:
         return f'<b>{get_wind_speed(forecast["wind_speed"])}</b>'


def forecast_template(forecast, period, location_name):
    if period == forecast_types['now']:
        return dedent(f"""
            Текущая погода для локации <b><i>{location_name}</i></b>:
            Температура: {render_temp(forecast)}
            Осадки: {render_cloudness(forecast)}
            Ветер: {render_wind(forecast)}
            Давление: <b>{forecast['pressure']} мм.рт.ст.</b>
            Влажность: <b>{forecast['humidity']}%</b>""")
    else:
        return dedent(f"""
            Погода на <b>{period}</b>, <b>{forecast['date']}</b> для локации <b><i>{location_name}</i></b>:
            Температура: {render_temp(forecast)}
            Осадки: {render_cloudness(forecast)}
            Ветер: {render_wind(forecast)}
            Влажность: <b>{forecast['humidity']}%</b>""")
