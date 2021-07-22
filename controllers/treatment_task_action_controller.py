#!/usr/bin/env python
from datetime import datetime
from os import stat
from controllers.errors import AuthError, BadRequestError, ForbiddenError, InternalError
from flask import Blueprint, jsonify, request, Response
from flask.globals import session
import services.dog_status_service as dog_status_service
import services.role_service as role_service
import services.treatment_task_service as treatment_task_service
import services.treatment_task_action_service as treatment_task_action_service
from werkzeug.exceptions import Forbidden, HTTPException
import json
from . import auth_helper, file_helper
from config import db

api = Blueprint('treatment_task_actions', 'treatment_task_actions')

@api.route('/treatment_task_actions/<string:treatment_task_id>', methods=['GET'])
def api_get_task_action(treatment_task_id):
    auth_helper.verify_auth(3)
    
    treatment_task_actions = treatment_task_action_service.getAll(treatment_task_id)
    enriched_treatment_task_actions = []
    for treatment_task_action in treatment_task_actions:
        if  treatment_task_action["action_photo"]:
            treatment_task_action["action_photo"] = request.host_url + treatment_task_action["action_photo"]
        enriched_treatment_task_actions.append(treatment_task_action)
    return jsonify(enriched_treatment_task_actions)

@api.route('/treatment_task_action', methods=['POST'])
def api_create_task_action():
    auth_helper.verify_auth(3)
    user = session['user']

    if not all(attr in request.form for attr in ["treatment_task_id", "action_performed"]):
        raise BadRequestError("Missing attributes")

    if request.form["action_performed"] == "":
        raise BadRequestError("Action performed cannot be empty")

    treatment_task = treatment_task_service.get(request.form["treatment_task_id"])
    if not treatment_task:
        raise BadRequestError("Invalid treatment task ID")

    dog_status = dog_status_service.getCurrentStatusForDog(treatment_task.tag)
    if not dog_status:
        raise BadRequestError("Cannot find dog status")
    elif dog_status.status != treatment_task.status:
        raise BadRequestError("Treatment task is not currently active. Dog is in a different status.")
    
    if treatment_task.is_completed:
        raise BadRequestError("Treatment task has already been completed.")
        
    role = role_service.get(treatment_task.assigned_role)
    if not role:
        raise BadRequestError("Invalid role")
    
    if user["role_level"] > role.level:
        raise Forbidden("Not authorized to act on this task")
    
    action_photo = ""
    if "action_photo" in request.files:
        action_photo = file_helper.upload_file('action_photo', treatment_task.tag, user["id"], "action")

    treatment_task = treatment_task_service.put({
        "id": request.form["treatment_task_id"],
        "is_completed": True,
        "last_modified_timestamp": datetime.utcnow(), 
        "last_modified_by": user["id"],
    })

    if not treatment_task:
        raise InternalError("Cannot save treatment task")

    if not treatment_task_action_service.get(request.form["treatment_task_id"]):
        treatment_task_action = treatment_task_action_service.post({
            "treatment_task_id": request.form["treatment_task_id"], 
            "action_performed": request.form["action_performed"], 
            "action_photo": action_photo, 
            "timestamp": datetime.utcnow(), 
            "by": user["id"]})
    else:
        treatment_task_action = treatment_task_action_service.put({
            "treatment_task_id": request.form["treatment_task_id"], 
            "action_performed": request.form["action_performed"], 
            "action_photo": action_photo, 
            "timestamp": datetime.utcnow(), 
            "by": user["id"]})

    if  treatment_task_action.action_photo:
        treatment_task_action.action_photo = request.host_url + treatment_task_action.action_photo
    db.session.commit()
    return jsonify(treatment_task_action.as_dict())


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