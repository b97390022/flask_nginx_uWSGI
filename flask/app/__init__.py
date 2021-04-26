from flask import Flask, abort, request, render_template, url_for, jsonify, flash, redirect, session, Blueprint

from flask_sqlalchemy import SQLAlchemy

from flask_migrate import Migrate

import logging
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler 
from flask.logging import create_logger
from flask_table import Table, Col
from app.script import run_prediction_web
from app.script import update_curation
#from script.required_attributes import *
from app.script import required_attributes as RA
import os
import pandas as pd
from time import sleep
from datetime import timedelta

from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from app.config.config import config

from app.view.email import email

db = SQLAlchemy()

mail = email()

login_manager = LoginManager()
login_manager.login_view = '/auth/login'
login_manager.login_message = u"Hello? Please log in to continue."
login_manager.login_message_category = "info"

    
def create_app(config_name):

    class LoginForm(FlaskForm):
        username = StringField('Username', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired()])
        remember_me = BooleanField('Remember Me')
        submit = SubmitField('Sign In')

    def register_blueprints(app):
        """Register blueprints with the Flask application."""
        from .view.auth import auth
        app.register_blueprint(auth, url_prefix='/auth')

    
    app = Flask(__name__)

    register_blueprints(app)
    
    app.secret_key = b'\xdd\x88w\x1a\x08;\xcaj\x99\xee|\xbbN\ns\xbe\xc8Z\x18\xa5nV2\xf4'

    # 設定config
    app.config.from_object(config['development']) 

    db.init_app(app)

    mail.init_app(app)

    login_manager.init_app(app)

    logger = create_logger(app)

    formatter = logging.Formatter("[%(asctime)s][%(filename)s:%(lineno)d][%(levelname)s][%(thread)d] - %(message)s")
    handler = TimedRotatingFileHandler("./app/logs/flask.log", when="midnight", interval=1, encoding="UTF-8")
    handler.suffix = "%Y%m%d"
    logger.addHandler(handler)
    handler.setFormatter(formatter)

    

    # 邦齊的部分

    di_config = RA.read_json(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'script/config_web.json')))
    path_model = run_prediction_web.get_latest_model(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'script', di_config.get('model')))
    model_gclf = RA.DeepGoogleSearch(path_model)


    # default to auth.login
    @app.route('/', methods=['GET'])
    def default():
        return redirect(url_for('auth.login'))

    @app.route('/index', methods=['GET','POST'])
    @login_required
    def index():
        if request.method == 'GET':
            logger.info('A debug message')

            return render_template('home.html')
        elif request.method == 'POST':
            # try:
            text = request.form['textbox']

            use_cache = False if request.form.get('use_cache') == None else True
            assist_curation = False if request.form.get('assist_curation') == None else True
            cache_date_limit = False if request.form.get('cache_date_limit') == None else int(request.form.get('cache_date_limit'))
            python_results, batchid, api_counts = run_prediction_web.main(text, model_gclf,num_search_page=1, path_config='config_web.json',use_cache=use_cache,assist_curation=assist_curation,cache_date_limit=cache_date_limit)

            df_api_counts = pd.DataFrame([[k, v] for k, v in api_counts.items()], columns=['api-name', 'usage'], index=list(range(len(api_counts))))
            
            return render_template("show_results.html", 
                html_records=[python_results.to_html(classes='data')], 
                titles=python_results.columns.values,
                data=python_results, 
                cols=python_results.columns,
                rows=python_results.shape[0],
                html_counts=[df_api_counts.to_html(classes='count')], 
                titles_counts=df_api_counts.columns.values,
                use_cache=use_cache,
                assist_curation=assist_curation,
                batchid=batchid)
            # except Exception as e:
            #     ms = f'Looks like you have some error: {repr(e)}'
            #     flash(ms)
            #     return redirect(url_for('index'))

    @app.route('/show_logs', methods=['GET'])
    def show_logs():
        if request.method == 'GET':
            return render_template('show_logs.html')

    @app.route('/submit', methods=['POST'])
    def submit():
        data = request.get_json()
        print(data)
        batchid = data.get('batchid')
        curation = {int(k):[True if v[1]=='True' else (False if v[3]=='True' else None), (v[-1] if v[-1]!="None" else '')] for k,v in data.items() if k!="batchid"}
        print(curation, batchid)
        # data = pd.DataFrame.from_dict(data)
        update_curation.update_curation(batchid, curation)
        return jsonify({'error':'missing data!'})

    return app, db




