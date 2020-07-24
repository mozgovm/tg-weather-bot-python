import mongoengine
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
db_name = 'py-weather-bot-users'
mongodb_uri = f'mongodb+srv://MyMongoDBUSER:{MONGODB_PASSWORD}@weatherbotdb-n7lcm.mongodb.net/{db_name}?retryWrites=true&w=majority'


class User(mongoengine.Document):
    userName = mongoengine.StringField(required=True, unique=True)
    lastLocations = mongoengine.ListField()
    meta = {'collection': 'users'}


def connect():
    mongoengine.connect(db_name, host=mongodb_uri)


def create_user(user_name):
    user = User()
    user.userName = user_name
    user.save()
    return user


def find_user(user_name):
    user = User.objects(userName=user_name).first()
    return user
