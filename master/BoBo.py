#!/usr/bin/env python2

import random
import string
import hashlib
from functools import wraps
import datetime
import os
import shutil
import tempfile

from flask import Flask
from flask_script import Manager

from models import db
from models import Bot
from models import Command
from UI import UI
from Utilities import Utilities
from config import config


app = Flask(__name__)
app.config.from_object(config['dev'])
app.register_blueprint(UI)
app.register_blueprint(Utilities, url_prefix="/Utilities")
db.init_app(app)
manager = Manager(app)


@app.after_request
def headers(response):
    response.headers["Server"] = "BoBo"
    return response


@manager.command
def initdb():
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    heroku_port = int(os.environ.get('PORT'))
    app.run(host='0.0.0.0', port=heroku_port)
    #manager.run()
