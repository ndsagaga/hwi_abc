from flask import session, request
from datetime import datetime

from werkzeug.exceptions import Forbidden
from . import user_controller
import services.user_session_service as user_session_service
import services.user_service as user_service
import services.role_service as role_service
from pytz import UTC
from . import errors
from config import db

def verify_auth(role_level=None):
    if not request.headers.has_key("Authorization"):
        raise errors.AuthError("No session key found!")
    
    session_key = request.headers.get('Authorization')
    print("Verifying session: " + session_key)
    user_session = user_session_service.get(session_key)
    if not user_session or user_session.expire_timestamp < datetime.utcnow():
        raise errors.AuthError("Invalid session")
    
    user = user_service._get(user_session.user_id)
    role = role_service.get(user.role)
    if role is None:
        raise errors.InternalError("Invalid role")
    if role_level and role.level > role_level:
        raise errors.ForbiddenError("Not Authorized")

    user_dict = user.as_dict()
    user_dict['session_key'] = session_key
    del user_dict['password_hash']
    user_dict["role_level"] = role.level

    session['user'] = user_dict
    
    db.session.commit()

    return True
    