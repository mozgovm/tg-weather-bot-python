import requests as req

supported_languages = ['Russian']


def get_cloudness_codes():
    url = 'http://www.weatherapi.com/docs/conditions.json'
    res = req.get(url)
    data = res.json()
    return data


def get_language_index(language, lang_list):
    for index, lang in enumerate(lang_list):
        if lang['lang_name'] == language:
            return index


def create_cloudness_object(data, lang_list):
    result = {}
    for code_object in data:
        code_propety_name = code_object['code']
        result[code_propety_name] = {}
        for lang in lang_list:
            index = get_language_index(lang, code_object['languages'])
            property_name = lang
            result[code_propety_name][property_name] = {
                'day_text': code_object['languages'][index]['day_text'],
                'night_text': code_object['languages'][index]['night_text']
            }
    return result
