#!/usr/bin/env python
from models.user import User
from config import db
from werkzeug.exceptions import NotFound

def get(id, password_hash):
    '''
    Get all entities
    :returns: all entity
    '''
    user = User.query.filter_by(id=id, password_hash=password_hash, is_active=True).first()
    return user

def _get(id):
    '''
    Get all entities
    :returns: all entity
    '''
    user = User.query.get(id)
    return user

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    user = User(**body)
    db.session.add(user)
    return user

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    user = User.query.get(body['id'])
    if user:
        user = User(**body)
        db.session.merge(user)
        db.session.flush()
        return user
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    user = User.query.get(id)
    if user:
        db.session.delete(user)
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


