#!/usr/bin/env python
from controllers.errors import AuthError, BadRequestError, ForbiddenError
from flask import Blueprint, jsonify, request, Response
from flask.globals import session
import services.dog_status_service as dog_status_service
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
    if new_dog_status.status == "FIT_FOR_SURGERY":
        _created_ffs_tasks(request.form["tag"])
    elif new_dog_status.status == "IN_SURGERY":
        _created_in_surgery_tasks(request.form["tag"])
    elif new_dog_status.status == "POST_SURGERY":
        _created_post_surgery_tasks(request.form["tag"])
    
    db.session.commit()
    return jsonify(new_dog_status.as_dict())

def _create_captured_tasks(tag):
    tasks = {
        "Notes about dog pick-up location.": "HANDLER", 
        "Record body temperature.": "SUPERVISOR", 
        "Record any external external wounds/bruises.": "SUPERVISOR", 
        "Additional notes for doctor.": "SUPERVISOR", 
        "Sign off on status change.": "DOCTOR"
        }
    for task, role in tasks.items():
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "CAPTURED", 
            "assigned_role": role, 
            "task": task, 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_active": True})
        if not treatment_task:
            return False
    
    return True

def _created_in_surgery_tasks(tag):
    tasks = {
        "Administer Xylazine.": "DOCTOR", 
        "Administer Atropine Sulphate.": "DOCTOR", 
        "Administer Thiosol.": "DOCTOR", 
        "Administer Ketamine.": "DOCTOR", 
        "Administer Ivermectin.": "DOCTOR", 
        "Administer Meloxicam.": "DOCTOR", 
        "Administer Vitamin.": "DOCTOR", 
        "Administer Penicillin.": "DOCTOR", 
        "Administer Diazepam.": "DOCTOR", 
        "Administer Cefotaxime.": "DOCTOR", 
        "Additional notes.": "SUPERVISOR", 
        "Sign off on status change.": "DOCTOR"
        }
    for task, role in tasks.items():
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "IN_SURGERY", 
            "assigned_role": role, 
            "task": task, 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_active": True})
        if not treatment_task:
            return False
    
    return True

def _created_post_surgery_tasks(tag):
    tasks = {
        "Record body temperature twice a day.": "SUPERVISOR", 
        "Record incision condition. Add photos.": "SUPERVISOR", 
        "Additional notes.": "SUPERVISOR", 
        "Sign off on status change.": "DOCTOR"
        }
    for task, role in tasks.items():
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "POST_SURGERY", 
            "assigned_role": role, 
            "task": task, 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_active": True})
        if not treatment_task:
            return False
    
    return True

def _created_ffs_tasks(tag):
    tasks = {
        "Shave surgery site.": "HANDLER", 
        "Ensure mouth guard and other safety harnesses are put on the dog.": "HANDLER", 
        "Sign off on status change.": "DOCTOR"
        }
    for task, role in tasks.items():
        treatment_task = treatment_task_service.post({
            "tag": tag, 
            "status": "POST_SURGERY", 
            "assigned_role": role, 
            "task": task, 
            "last_modified_timestamp": datetime.utcnow(), 
            "last_modified_by": "nirup",
            "is_active": True})
        if not treatment_task:
            return False
    
    return True


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