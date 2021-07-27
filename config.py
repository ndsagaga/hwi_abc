#!/usr/bin/env python
import os
import yaml
from flask import Flask, sessions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask.json import JSONEncoder
from datetime import date


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat() + 'Z'
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

HOST_ADDRESS = "http://192.168.1.203:5000"
config_obj = yaml.load(open('config.yaml'), Loader=yaml.Loader)

# override the environment variables
database_url = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_DATABASE_URI'] = config_obj['SQLALCHEMY_DATABASE_URI'] if database_url is None else database_url
app.secret_key = config_obj['SESSION_SECRET']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class CustomSessionInterface(sessions.SecureCookieSessionInterface):
    """Disable default cookie generation."""
    def should_set_cookie(self, *args, **kwargs):
        return False

    """Prevent creating session from API requests."""
    def save_session(self, *args, **kwargs):
        return super(CustomSessionInterface, self).save_session(*args,
                                                                **kwargs)

app.session_interface = CustomSessionInterface()
