
#!/usr/bin/env python
from models.dog import Dog
from config import db
from werkzeug.exceptions import NotFound
from sqlalchemy import or_
from models.dog_status import DogStatus
from . import dog_status_service

def getAll():
    '''
    Get all entities
    :returns: all entity
    '''
    return Dog.query.all()

def get(tag):
    '''
    Get all entities
    :returns: all entity
    '''
    return Dog.query.get(tag)

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    dog = Dog(**body)
    db.session.add(dog)
    return dog

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    dog = Dog.query.get(body['tag'])
    if dog:
        dog = Dog(**body)
        db.session.merge(dog)
        db.session.flush()
        return dog
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    dog = Dog.query.get(id)
    if dog:
        db.session.delete(dog)
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


