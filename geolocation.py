import requests as req
import urllib.parse as parse


def get_coords_by_location_name(received_location):
    url = f'http://search.maps.sputnik.ru/search/addr?q={parse.quote(received_location)}'
    res = req.get(url)
    geodata = res.json()
    address = geodata['result']['address']

    if not address:
        return

    coords = address[0]['features'][0]['geometry']['geometries'][0]['coordinates']
    location_name = address[0]['features'][0]['properties']['title']

    return coords, location_name


def get_location_name(lat, lon):
    url = f'http://whatsthere.maps.sputnik.ru/point?lat={lat}&lon={lon}'
    res = req.get(url)
    geodata = res.json()
    address = geodata['result']['address']

    if not address:
        return

    location_name = address[0]['features'][0]['properties']['title']
    return location_name


def get_index_of_location(last_locations, location_name):
    result = []
    for i, location in enumerate(last_locations):
        result.append(location['locationName'] == location_name)
    if True in result:
        return result.index(True)
    else:
        return -1


def move_location(locations, current_index, new_index=0):
    if current_index == new_index:
        return

    locations.insert(new_index, locations.pop(current_index))
