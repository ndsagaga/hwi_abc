#!/usr/bin/env python
from datetime import date, datetime
from controllers.errors import AuthError, BadRequestError, ForbiddenError
from flask import Blueprint, jsonify, request, Response
from flask.globals import session
import services.dog_status_service as dog_status_service
import services.dog_service as dog_service
import services.role_service as role_service
import services.treatment_task_service as treatment_task_service
import services.treatment_task_action_service as treatment_task_action_service
from werkzeug.exceptions import HTTPException
import json
from . import auth_helper, file_helper
from config import db
import time

api = Blueprint('treatment_tasks', 'treatment_tasks')

@api.route('/treatment_tasks/<string:tag>', methods=['GET'])
def api_get_task(tag):
    auth_helper.verify_auth(1)
    user = session['user']

    dog = dog_service.get(tag)
    if not dog:
        raise BadRequestError("Invalid dog tag")

    dog_status = dog_status_service.getCurrentStatusForDog(tag)
    if not dog_status:
        raise BadRequestError("Cannot find dog status")
    
    treatment_tasks = treatment_task_service.getForDogAndStatus(dog.tag, dog_status.status)
    enriched_treatment_tasks = []
    for treatment_task in treatment_tasks:
        treatment_task = treatment_task.as_dict()
        treatment_task_actions = treatment_task_action_service.getAll(treatment_task["id"])
        treatment_task["actions"] = []
        for treatment_task_action in treatment_task_actions:
            treatment_task_action = treatment_task_action.as_dict()
            if treatment_task_action["action_photo"]:
                treatment_task_action["action_photo"] = request.host_url + treatment_task_action["action_photo"]
            
            treatment_task["actions"].append(treatment_task_action)
        enriched_treatment_tasks.append(treatment_task)

    return jsonify(enriched_treatment_tasks)

@api.route('/treatment_task', methods=['POST'])
def api_create_task():
    auth_helper.verify_auth(1)
    user = session['user']

    if not all(attr in request.form for attr in ["tag", "status", "assigned_role", "task"]):
        raise BadRequestError("Missing attributes")

    dog = dog_service.get(request.form["tag"])
    if not dog:
        raise BadRequestError("Invalid dog tag")

    dog_status = dog_status_service.getCurrentStatusForDog(request.form["tag"])
    if dog_status:
        if dog_status.status != request.form["status"]:
            raise BadRequestError("Tasks can only be created for the current status of dog")
    else:
        raise BadRequestError("Cannot find dog status")
    
    if request.form["assigned_role"] not in ["DOCTOR", "SUPERVISOR", "HANDLER"]:
        raise BadRequestError("Invalid assigned role")

    treatment_task = treatment_task_service.post({
        "tag": request.form["tag"], 
        "status": request.form["status"], 
        "assigned_role": request.form["assigned_role"], 
        "task": request.form["task"], 
        "last_modified_timestamp": datetime.utcnow(), 
        "last_modified_by": user["id"],
        "is_active": True})

    db.session.commit()
    return jsonify(treatment_task.as_dict())


@api.route('/treatment_task/mark_complete', methods=['POST'])
def api_mark_task_complete():
    auth_helper.verify_auth()
    user = session['user']

    if "treatment_task_id" not in request.form:
        raise BadRequestError("No treatment task ID found")

    treatment_task = treatment_task_service.get(request.form["treatment_task_id"])
    if not treatment_task:
        raise BadRequestError("Invalid treatment task ID")
        
    role = role_service.get(treatment_task.assigned_role)
    if not role:
        raise BadRequestError("Invalid role")
    
    if user["role_level"] > role.level:
        raise ForbiddenError("Not authorized to act on this task")
    
    if treatment_task.is_completed:
        raise BadRequestError("Task already completed.")
    
    treatment_task.is_completed = True
    treatment_task.last_modified_timestamp = datetime.utcnow()
    treatment_task.last_modified_by = user['id']

    treatment_task = treatment_task_service.put(treatment_task.as_dict())
    db.session.commit()
    return jsonify(treatment_task.as_dict())


@api.route('/treatment_task/mark_incomplete', methods=['POST'])
def api_mark_task_incomplete():
    auth_helper.verify_auth()
    user = session['user']

    if "treatment_task_id" not in request.form:
        raise BadRequestError("No treatment task ID found")

    treatment_task = treatment_task_service.get(request.form["treatment_task_id"])
    if not treatment_task:
        raise BadRequestError("Invalid treatment task ID")
        
    role = role_service.get(treatment_task.assigned_role)
    if not role:
        raise BadRequestError("Invalid role")
    
    if user["role_level"] > role.level:
        raise ForbiddenError("Not authorized to act on this task")
    
    if not treatment_task.is_completed:
        raise BadRequestError("Task already incomplete.")
    
    treatment_task.is_completed = False
    treatment_task.last_modified_timestamp = datetime.utcnow()
    treatment_task.last_modified_by = user['id']

    treatment_task = treatment_task_service.put(treatment_task.as_dict())
    db.session.commit()
    return jsonify(treatment_task.as_dict())


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