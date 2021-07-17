#!/usr/bin/env python
from flask.helpers import send_from_directory
from controllers.errors import AuthError, BadRequestError, ForbiddenError, InternalError
from flask.wrappers import Response
from models.role import Role
from flask import Blueprint, jsonify, request, session
import services.user_service as user_service
import services.user_session_service as user_session_service
import services.role_service as role_service
from models.user import User
from werkzeug.exceptions import HTTPException
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from . import auth_helper
from config import db

api = Blueprint('users', 'users')


@api.route('/hash/<string:msg>', methods=['GET'])
def hash(msg):
    ''' Get all entities'''
    hashed_password = hashlib.sha512(msg.encode('utf-8')).hexdigest()
    return hashed_password

@api.route('/login', methods=['POST'])
def api_login():
    user = user_service.get(id=request.form['id'], password_hash=hashlib.sha512(
        request.form['password'].encode('utf-8')).hexdigest())
    if not user:
        raise BadRequestError("Invalid login.")
    user_session_service.delete_user_sessions(user.id)
    session_key = str(uuid.uuid4())
    role = role_service.get(user.role)
    if role is None:
        raise InternalError("Invalid role")

    user_dict = user.as_dict()
    user_dict['session_key'] = session_key
    del user_dict['password_hash']
    user_dict['expire_timestamp'] = (datetime.utcnow() + timedelta(days=7))
    user_dict["role_level"] = role.level

    session['user'] = user_dict
    user_session_service.post(
        {"id": session_key, "user_id": user_dict['id'], "expire_timestamp": user_dict["expire_timestamp"]})
    print("Logged in successfully!")
    print(user_dict)

    db.session.commit()
    return jsonify(user_dict)


@api.route('/login', methods=['GET'])
def api_login_session():
    if auth_helper.verify_auth():
        return jsonify(session['user'])
    raise AuthError("Invalid session")


@api.route('/logout', methods=['GET'])
def api_logout_session():
    if auth_helper.verify_auth():
        user_session_service.delete_user_sessions(session['user']["id"])
    return jsonify({})


@api.route('/photos/<path:path>')
def send_js(path):
    return send_from_directory('photos', path)


@api.errorhandler(AuthError)
@api.errorhandler(ForbiddenError)
@api.errorhandler(BadRequestError)
def handle_exception(e):
    """Return JSON format for HTTP errors."""
    # start with the correct headers and status code from the error
    response = Response(json.dumps({
        'success': False,
        "message": e.message
    }), status=e.code, mimetype="application/json")
    return response
