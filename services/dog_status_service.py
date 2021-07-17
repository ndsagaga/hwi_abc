
#!/usr/bin/env python
from models.dog import Dog
from models.dog_status import DogStatus
from config import db
from werkzeug.exceptions import NotFound
from sqlalchemy import func

def getCurrentStatusForDog(tag):
    '''
    Get all entities
    :returns: all entity
    '''
    return DogStatus.query.filter_by(tag=tag).order_by(DogStatus.timestamp.desc()).first()

def getForAllDogs():
    latest_dog_statuses = db.engine.execute("SELECT t1.* FROM dog_status t1   JOIN (SELECT tag, MAX(timestamp) timestamp FROM dog_status GROUP BY tag) t2     ON t1.tag = t2.tag AND t1.timestamp = t2.timestamp;")
    return latest_dog_statuses

def getAll():
    latest_dog_statuses = db.engine.execute("SELECT * FROM dog_status ORDER BY tag ASC, timestamp DESC")
    return latest_dog_statuses
    
def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    dog_status = DogStatus(**body)
    db.session.add(dog_status)
    return dog_status

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    dog_status = DogStatus.query.get(body['id'])
    if dog_status:
        dog_status = DogStatus(**body)
        db.session.merge(dog_status)
        db.session.flush()
        return dog_status
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    dog_status = DogStatus.query.get(id)
    if dog_status:
        db.session.delete(dog_status)
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


