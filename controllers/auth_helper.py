from flask import session, request
from datetime import datetime
from . import user_controller
from pytz import UTC

def verify_auth(role_level=None):
    session_key = request.headers.get('Authorization')
    if session_key not in session:
        raise RuntimeError("User not authenticated")
    if session[session_key]["expire_timestamp"] < UTC.localize(datetime.now()):
        user_controller.api_logout_session(session_key)
        raise RuntimeError("User not authenticated")
    if not all(attr in session[session_key] for attr in ['id', 'first_name', 'last_name', 'role', 'role_level', 'is_active']):
        raise RuntimeError("User not authenticated")
    
    if role_level is not None and session[session_key]["role_level"] > role_level:
        raise RuntimeError("Not Authorized")

    return True
    