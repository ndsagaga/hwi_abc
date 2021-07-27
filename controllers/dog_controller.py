#!/usr/bin/env python
from flask.wrappers import Response
from controllers.errors import AuthError, BadRequestError, ForbiddenError
from flask import Blueprint, jsonify, request
from flask.globals import session
import services.dog_service as dog_service
from werkzeug.exceptions import HTTPException
import json
from . import auth_helper, file_helper
from datetime import date, datetime
import services.dog_status_service as dog_status_service
from . import dog_status_controller
from config import db

api = Blueprint('dogs', 'dogs')

@api.route('/dogs', methods=['GET'])
def api_list_dogs():
    auth_helper.verify_auth()
    user = session['user']
    dogs = dog_service.getAll()
    dog_dicts = [dog.as_dict() for dog in dogs]
    #print(dog_dicts)
    statuses = dog_status_service.getAll()
    status_dict = dict()
    for status in statuses:
        if status.tag not in status_dict:
            status_dict[status.tag] = []
        status_dict[status.tag].append([status.status, status.timestamp])
    
    filtered_dog_dicts = []
    for dog_dict in dog_dicts:
        dog_dict["status"] = status_dict[dog_dict["tag"]][0][0]

        if user["role_level"] >= 3 and dog_dict["status"] not in ["CAPTURED", "FIT_FOR_RELEASE"]:
            continue
        dog_dict["status_history"] = status_dict[dog_dict["tag"]]

        if dog_dict["pickup_photo"]:
            dog_dict["pickup_photo"] = request.host_url + dog_dict["pickup_photo"]
        dog_dict["time"] = datetime.utcnow()
        filtered_dog_dicts.append(dog_dict)

    return jsonify(filtered_dog_dicts)

@api.route('/dog', methods=['POST'])
def api_create_dog():
    auth_helper.verify_auth(role_level=3.0)
    user = session['user']

    if not all(attr in request.form for attr in ["tag", "gender", "age_category", "color", "pickup_lat", "pickup_long", "pickup_time"]):
        raise BadRequestError("Missing attributes")

    dog = dog_service.get(request.form["tag"])
    if dog:
        raise BadRequestError("Tag already exists")

    new_dog = dict()
    new_dog["tag"] = request.form["tag"]
    
    if "avatar" in request.files:
        new_dog["avatar"] = file_helper.upload_file('avatar', new_dog["tag"], user["id"], "avatar")
    new_dog["gender"] = request.form["gender"]
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

    new_dog["created_timestamp"] = datetime.utcnow()
    new_dog["last_modified_timestamp"] = datetime.utcnow()
    new_dog = dog_service.post(new_dog)
    new_dog = new_dog.as_dict()
    print(new_dog)
    if new_dog["avatar"]:
        new_dog["avatar"] = request.host_url + new_dog["avatar"]

    dog_status_service.post({"tag": new_dog["tag"], "status": "CAPTURED", "timestamp": datetime.utcnow(), "by": user["id"]})
    db.session.commit()
    return jsonify(new_dog)

@api.route('/dog/edit', methods=['POST'])
def api_edit_dog():
    auth_helper.verify_auth(role_level=2.0)
    print(request.files)
    user = session['user']
    if "tag" not in request.form:
        raise BadRequestError("Need dog tag")
    dog = dog_service.get(request.form["tag"])
    if not dog:
        raise BadRequestError("Invalid tag")
    
    new_dog = dog.as_dict()
    for attr in ["gender", "age_category", "color", "weight", "additional_info", "pickup_photo"]:
        if attr in request.form:
            new_dog[attr] = request.form[attr]
    
    if "pickup_photo" in request.files:
        new_dog["pickup_photo"] = file_helper.upload_file('pickup_photo', new_dog["tag"], user["id"], "pick_drop")
    
    new_dog["last_modified_timestamp"] = datetime.utcnow()

    new_dog = dog_service.put(new_dog)
    new_dog = new_dog.as_dict()
    new_dog["pickup_photo"] = request.host_url + new_dog["pickup_photo"]

    db.session.commit()
    return jsonify(new_dog)


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