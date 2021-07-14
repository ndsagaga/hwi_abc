#!/usr/bin/env python
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

api = Blueprint('users', 'users')


@api.route('/hash/<string:msg>', methods=['GET'])
def hash(msg):
    ''' Get all entities'''
    hashed_password = hashlib.sha512(msg.encode('utf-8')).hexdigest()
    return hashed_password


def login2():
    user_session_service.delete_user_sessions(request.json['id'])
    user_session_service.post({"id": "2", "user_id": "1", "expire_timestamp": (
        datetime.now() + timedelta(days=7))})
    user_sessions = user_session_service.getUserSessions(request.json['id'])
    return {"sessions": [x.as_dict() for x in user_sessions] if user_sessions else []}


@api.route('/login', methods=['POST'])
def api_login():
    user = user_service.get(id=request.form['id'], password_hash=hashlib.sha512(
        request.form['password'].encode('utf-8')).hexdigest())
    if not user:
        raise LookupError("User not found")
    user_session_service.delete_user_sessions(user.id)
    session_key = str(uuid.uuid4())
    role = role_service.get(user.role)
    if role is None:
        raise ValueError("Invalid role")

    user_dict = user.as_dict()
    user_dict['session_key'] = session_key
    del user_dict['password_hash']
    user_dict['expire_timestamp'] = (datetime.now() + timedelta(days=7))
    user_dict["role_level"] = role.level

    session[session_key] = user_dict
    user_session_service.post(
        {"id": session_key, "user_id": user_dict['id'], "expire_timestamp": user_dict["expire_timestamp"]})
    return jsonify(user_dict)


@api.route('/login', methods=['GET'])
def api_login_session():
    if auth_helper.verify_auth():
        return jsonify(session[request.headers.get("Authorization")])
    raise ValueError("Invalid session")


@api.route('/logout/<string:session_key>', methods=['GET'])
def api_logout_session(session_key):
    if session_key not in session:
        return jsonify({})

    user_session_service.delete_user_sessions(session[session_key]['id'])
    return jsonify({})


@api.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON format for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        'success': False,
        "message": e.description
    })
    response.content_type = "application/json"
    return response
