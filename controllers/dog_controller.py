#!/usr/bin/env python
from flask import Blueprint, jsonify, request
from flask.globals import session
import services.dog_service as dog_service
from werkzeug.exceptions import HTTPException
import json
from . import auth_helper, file_helper
from datetime import date, datetime
import services.dog_status_service as dog_status_service

api = Blueprint('dogs', 'dogs')

@api.route('/dogs', methods=['GET'])
def api_list_dogs():
    auth_helper.verify_auth()
    user = session[request.headers.get('Authorization')]
    dogs = []
    if user["role_level"] >= 3:
        dogs = dog_service.getForHandlers()
    else:
        dogs = dog_service.getAll()
    return jsonify([dog.as_dict() for dog in dogs])

@api.route('/dog', methods=['POST'])
def api_create_dog():
    auth_helper.verify_auth(role_level=3.0)
    user = session[request.headers.get('Authorization')]

    if not all(attr in request.form for attr in ["tag", "gender", "age", "age_category", "color", "pickup_lat", "pickup_long", "pickup_time"]):
        raise ValueError("Missing attributes")

    new_dog = dict()
    new_dog["tag"] = request.form["tag"]
    
    if "avatar" in request.files:
        new_dog["avatar"] = file_helper.upload_file('avatar', new_dog["tag"], user["id"], "avatar")
    new_dog["gender"] = request.form["gender"]
    new_dog["age"] = request.form["age"]
    new_dog["age_category"] = request.form["age_category"]
    new_dog["color"] = request.form["color"]
    if "weight" in request.form:
        new_dog["weight"] = request.form["weight"]
    if "breed" in request.form:
        new_dog["breed"] = request.form["breed"]
    new_dog["pickup_lat"] = request.form["pickup_lat"]
    new_dog["pickup_long"] = request.form["pickup_long"]
    new_dog["pickup_time"] = datetime.utcfromtimestamp(int(request.form["pickup_time"]))
    new_dog["pickup_by"] = user["id"]
    new_dog["pickup_photo"] = file_helper.upload_file('pickup_photo', new_dog["tag"], user["id"], "pick_drop")

    new_dog["created_timestamp"] = datetime.now()
    new_dog["last_modified_timestamp"] = datetime.now()
    new_dog = dog_service.post(new_dog)

    dog_status_service.post({"tag": new_dog.tag, "status": "CAPTURED", "timestamp": datetime.now(), "by": user["id"]})

    return jsonify(new_dog.as_dict())

@api.route('/dog/edit', methods=['POST'])
def api_edit_dog():
    auth_helper.verify_auth(role_level=2.0)
    user = session[request.headers.get('Authorization')]
    if "tag" not in request.form:
        raise ValueError("Need dog tag")
    dog = dog_service.get(request.form["tag"])
    if not dog:
        raise ValueError("Invalid tag")
    
    new_dog = dog.as_dict()
    for attr in ["gender", "age", "age_category", "color", "weight", "breed", "is_vaccinated", "is_sterlized"]:
        if attr in request.form:
            new_dog[attr] = request.form[attr]
    
    if "avatar" in request.files:
        new_dog["avatar"] = file_helper.upload_file('avatar', new_dog["tag"], user["id"], "avatar")
    
    new_dog["last_modified_timestamp"] = datetime.now()

    new_dog = dog_service.put(new_dog)

    return jsonify(new_dog.as_dict())

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