
#!/usr/bin/env python
from models.user_session import UserSession
from config import db
from werkzeug.exceptions import NotFound
from flask import session

def get(session_key):
    '''
    Get all entities
    :returns: all entity
    '''
    return UserSession.query.get(session_key)

def getUserSessions(user_id):
    '''
    Get all entities
    :returns: all entity
    '''
    return UserSession.query.filter_by(user_id=user_id)

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    user_session = UserSession(id=body['id'], user_id=body['user_id'], expire_timestamp=body['expire_timestamp'])
    db.session.add(user_session)
    db.session.commit()
    return user_session

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    user_session = UserSession.query.get(body['id'])
    if user_session:
        user_session = UserSession(**body)
        db.session.merge(user_session)
        db.session.flush()
        db.session.commit()
        return user_session
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete_user_sessions(user_id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    user_sessions = UserSession.query.filter_by(user_id = user_id).all()
    
    if user_sessions:
        for user_session in user_sessions:
            db.session.delete(user_session)
            db.session.commit()
            if user_session.id in session:
                del session[user_session.id]
    return {'success': True}


