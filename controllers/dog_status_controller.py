#!/usr/bin/env python
from flask import Blueprint, jsonify, request
from flask.globals import session
import services.dog_status_service as dog_status_service
import services.status_service as status_service
from werkzeug.exceptions import HTTPException
import json
from . import auth_helper, file_helper
from datetime import date, datetime

api = Blueprint('dog_status', 'dog_status')

@api.route('/dog_status/<string:tag>', methods=['GET'])
def api_get_dog_status(tag):
    auth_helper.verify_auth()
    user = session[request.headers.get('Authorization')]
    dog_status = dog_status_service.getCurrentStatusForDog(tag)
    return jsonify(dog_status.as_dict())

@api.route('/dog_status', methods=['POST'])
def api_create_dog_status():
    auth_helper.verify_auth()
    user = session[request.headers.get('Authorization')]

    if not all(x in request.form for x in ["tag", "status"]):
        raise ValueError("Missing attributes")

    if request.form["status"] != "RELEASED" and user["role_level"] >= 3:
        raise LookupError("Unauthorized to change status")

    dog_status = dog_status_service.getCurrentStatusForDog(request.form["tag"])
    if not dog_status:
        raise ValueError("Dog does not have a previous status")
    old_dog_status = status_service.get(dog_status.status)
    new_dog_status = status_service.get(request.form["status"])
    if new_dog_status.order - old_dog_status.order not in [1.0, -1.0]:
        raise ValueError("Can only move by one step.")
    
    new_dog_status = dog_status_service.post({"tag": request.form["tag"], "status": request.form["status"], "timestamp": datetime.now(), "by": user["id"]})
    return jsonify(new_dog_status.as_dict())


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