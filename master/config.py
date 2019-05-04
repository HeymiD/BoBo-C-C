import random
import string


class Config:
    SECRET_KEY = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(60))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///BoBo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'uploads'


class Development(Config):
    DEBUG = True


config = {
    'dev': Development,
}
