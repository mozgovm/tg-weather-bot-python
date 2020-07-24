from bot import bot
import db
from geolocation import get_coords_by_location_name, get_index_of_location, move_location


def save_location(message):
    received_location = message.text
    coords, location_name = get_coords_by_location_name(received_location)

    if not coords:
        bot.send_message(
            message.chat.id, f'По запросу "{received_location}" не найдено ни одной локации, попробуйте еще раз'
        )
        return False

    longitude, latitude = coords
    db_user = db.find_user(message.from_user.username)

    if not db_user.lastLocations:
        db_user.lastLocations.append({
            'locationName': location_name,
            'lat': latitude,
            'lon': longitude
        })
    else:
        location_index = get_index_of_location(db_user.lastLocations, location_name)

        if location_index == -1:
            db_user.lastLocations.insert(0, {
                'locationName': location_name,
                'lat': latitude,
                'lon': longitude
            })
        else:
            move_location(db_user.lastLocations, location_index)

    while len(db_user.lastLocations) > 3:
        del db_user.lastLocations[-1]

    db_user.save()

    return location_name
