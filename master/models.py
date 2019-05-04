import random
import string
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Bot(db.Model):
    __tablename__ = 'bots'
    id = db.Column(db.String(100), primary_key=True)
    bot_name = db.Column(db.String(100))
    last_online = db.Column(db.DateTime())
    ip_address = db.Column(db.String(100))
    output = db.Column(db.Text(), default="")
    hostname = db.Column(db.String(100))
    username = db.Column(db.String(100))

    def __init__(self, uid):
        self.id = uid
        self.bot_name = self.id

    def push_command(self, cmdline):
        cmd = Command()
        cmd.bot = self
        cmd.cmdline = cmdline
        cmd.timestamp = datetime.now()
        db.session.add(cmd)
        db.session.commit()

    def is_online(self):
        return (datetime.now() - self.last_online).seconds < 15



class Command(db.Model):
    __tablename__ = 'commands'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bot_id = db.Column(db.Integer(), db.ForeignKey('bots.id'))
    bot = db.relationship('Bot', backref=db.backref('commands', lazy='dynamic'))
    cmdline = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime(), default=datetime.now)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    salt = db.Column(db.String(100))
    last_login_time = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
