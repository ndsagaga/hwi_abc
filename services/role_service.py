
#!/usr/bin/env python
from models.role import Role
from config import db
from werkzeug.exceptions import NotFound

def get(role):
    '''
    Get all entities
    :returns: all entity
    '''
    return Role.query.get(role)

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    role = Role(**body)
    db.session.add(role)
    db.session.commit()
    return role

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    role = Role.query.get(body['id'])
    if role:
        role = Role(**body)
        db.session.merge(role)
        db.session.flush()
        db.session.commit()
        return role
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    role = Role.query.get(id)
    if role:
        db.session.delete(role)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


