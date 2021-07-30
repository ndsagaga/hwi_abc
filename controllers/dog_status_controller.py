#!/usr/bin/env python
from controllers.errors import AuthError, BadRequestError, ForbiddenError
from flask import Blueprint, jsonify, request, Response
from flask.globals import session
import services.dog_status_service as dog_status_service
import services.dog_service as dog_service
import services.treatment_task_service as treatment_task_service
import services.status_service as status_service
from werkzeug.exceptions import HTTPException
import json
from . import auth_helper, file_helper
from datetime import date, datetime
from config import db

api = Blueprint('dog_status', 'dog_status')

@api.route('/dog_status/<string:tag>', methods=['GET'])
def api_get_dog_status(tag):
    auth_helper.verify_auth()
    dog_status = dog_status_service.getCurrentStatusForDog(tag)
    if dog_status:
        return jsonify(dog_status.as_dict())
    else:
        raise BadRequestError("Cannot find dog status")

@api.route('/dog_status', methods=['POST'])
def api_create_dog_status():
    auth_helper.verify_auth()
    user = session['user']

    if not all(x in request.form for x in ["tag", "status"]):
        raise BadRequestError("Missing attributes")

    if request.form["status"] != "RELEASED" and user["role_level"] >= 3:
        raise ForbiddenError("Unauthorized to change status")

    dog = dog_service.get(request.form["tag"])
    if not dog:
        raise BadRequestError("Dog does not exist")

    dog_status = dog_status_service.getCurrentStatusForDog(request.form["tag"])
    if not dog_status:
        raise BadRequestError("Dog does not have a previous status")
    old_dog_status = status_service.get(dog_status.status)
    new_dog_status = status_service.get(request.form["status"])
    if new_dog_status.order - old_dog_status.order != 1:
        raise BadRequestError("Can only move by one step.")
    
    treatment_tasks = treatment_task_service.getForDogAndStatus(request.form["tag"], old_dog_status.status)
    if treatment_tasks:
        for treatment_task in treatment_tasks:
            if not treatment_task.is_completed:
                raise BadRequestError("There are incomplete tasks in current status.")
    
    
    new_dog_status = dog_status_service.post({"tag": request.form["tag"], "status": request.form["status"], "timestamp": datetime.utcnow(), "by": user["id"]})
    if new_dog_status.status == "PRE_SURGERY":
        _created_pre_tasks(request.form["tag"], dog.weight)
    elif new_dog_status.status == "IN_SURGERY":
        _created_in_surgery_tasks(request.form["tag"], dog.weight)
    elif new_dog_status.status == "POST_SURGERY":
        _created_post_surgery_tasks(request.form["tag"])
    
    db.session.commit()
    return jsonify(new_dog_status.as_dict())

@api.route('/dog_status/release', methods=['POST'])
def api_create_dog_status_release():
    auth_helper.verify_auth()
    user = session['user']
    print(request.form)

    if not all(x in request.form for x in ["tag", "dropoff_lat", "dropoff_long"]):
        raise BadRequestError("Missing attributes")

    if user["role_level"] >= 3:
        raise ForbiddenError("Unauthorized to change status")

    dog = dog_service.get(request.form["tag"])
    if not dog:
        raise BadRequestError("Dog does not exist")

    dog_status = dog_status_service.getCurrentStatusForDog(request.form["tag"])
    if not dog_status:
        raise BadRequestError("Dog does not have a previous status")
    old_dog_status = status_service.get(dog_status.status)
    new_dog_status = status_service.get("RELEASED")
    if new_dog_status.order - old_dog_status.order != 1:
        raise BadRequestError("Can only move by one step.")
    
    treatment_tasks = treatment_task_service.getForDogAndStatus(request.form["tag"], old_dog_status.status)
    if treatment_tasks:
        for treatment_task in treatment_tasks:
            if not treatment_task.is_completed:
                raise BadRequestError("There are incomplete tasks in current status.")
    
    if "dropoff_photo" not in request.files:
        raise BadRequestError("No photo attached")

    dropoff_photo = file_helper.upload_file('dropoff_photo', dog.tag, user["id"], "pick_drop")
    
    new_dog_status = dog_status_service.post({"tag": request.form["tag"], "status": "RELEASED", "timestamp": datetime.utcnow(), "by": user["id"]})
    dog_updated = dog_service.put({"tag": request.form["tag"], 
                "last_modified_timestamp": datetime.utcnow(), 
                "dropoff_lat": request.form["dropoff_lat"],
                "dropoff_long": request.form["dropoff_long"],
                "dropoff_time": datetime.utcnow(),
                "dropoff_by": user['id'],
                "dropoff_photo": dropoff_photo
                })
    
    db.session.commit()
    return jsonify({})


def _created_in_surgery_tasks(tag,  weight):
    tasks = [
        {
            "assigned_role": "SUPERVISOR",
            "task": "Attending doctor's name",
            "response_type": "TEXT",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Surgery start time",
            "response_type": "TIMESTAMP",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("ceftriaxone", weight) + " of Ceftriaxone",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Topups",
            "response_type": "COUNTER",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Surgery end time",
            "response_type": "TIMESTAMP",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Additional notes",
            "response_type": "TEXT",
            "is_required": False
        }
    ]
    for task in tasks:
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "IN_SURGERY", 
            "assigned_role": task["assigned_role"], 
            "task": task["task"], 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_required": task["is_required"],
            "response_type": task["response_type"]})
        if not treatment_task:
            return False
    
    return True

def _created_post_surgery_tasks(tag):
    tasks = [
        {
            "assigned_role": "SUPERVISOR",
            "task": "Additional notes",
            "response_type": "TEXT",
            "is_required": False
        }
    ]
    for task in tasks:
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "POST_SURGERY", 
            "assigned_role": task["assigned_role"], 
            "task": task["task"], 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_required": task["is_required"],
            "response_type": task["response_type"]})
        if not treatment_task:
            return False
    
    return True

def _created_pre_tasks(tag, weight):
    if not weight:
        raise BadRequestError("Dog needs to have a weight set.")
    tasks = [
        {
            "assigned_role": "SUPERVISOR",
            "task": "Apply eye ointment",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Cut ear for identification",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Shave & sterlize surgery site",
            "response_type": "BINARY",
            "is_required": True 
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Empty the dog's bladder",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("xylozine", weight) + " of Xylozine",
            "response_type": "BINARY",
            "is_required": True
        },
        { 
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("ketamine", weight) + " of Ketamine",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("melonex", weight) + " of Melonex",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("ivermectin", weight) + " of Ivermectin",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("penicillin", weight) + " of Penicillin",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("belamyl", weight) + " of Belamyl",
            "response_type": "BINARY",
            "is_required": True
        },
        {
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("atropine", weight) + " of Atropine Sulphate",
            "response_type": "BINARY",
            "is_required": True
        },
        { 
            "assigned_role": "SUPERVISOR",
            "task": "Administer " + _getDosage("diazepam", weight) + " of Diazepam",
            "response_type": "BINARY",
            "is_required": True
        }
    ]
    for task in tasks:
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "PRE_SURGERY", 
            "assigned_role": task["assigned_role"], 
            "task": task["task"], 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_required": task["is_required"],
            "response_type": task["response_type"]})
        if not treatment_task:
            return False
    
    return True

def _getDosage(medicine, weight): 
    if medicine == "xylozine":
        if weight < 10:
            return str(round(weight/10, 2)) + " ml"
        elif weight <= 20:
            return "1 ml"
        elif weight < 30:
            return "1." + str(round((weight-20)/10, 2)) + " ml"
        else:
            return "2 ml"
    elif medicine == "ketamine":
        return str(round(0.2 * weight, 2)) + " ml"
    elif medicine == "melonex":
        return str(round(0.04 * weight, 2)) + " ml"
    elif medicine == "ivermectin":
        return str(round(0.03 * weight, 2)) + " ml"
    elif medicine == "penicillin":
        return str(round(0.2 * weight, 2)) + " ml"
    elif medicine == "belamyl":
        return str(round(0.03 * weight, 2)) + " ml"
    elif medicine == "diazepam":
        return str(round(0.05 * weight, 2)) + " ml"
    elif medicine == "atropine":
        return str(round(0.0832 * weight, 2)) + " ml"
    elif medicine == "ceftriaxone":
        return str(round(0.1 * weight, 2)) + " ml"
    return "X ml"

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