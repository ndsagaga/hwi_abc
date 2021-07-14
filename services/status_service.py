
#!/usr/bin/env python
from models.status import Status
from config import db
from werkzeug.exceptions import NotFound

def get(status):
    '''
    Get all entities
    :returns: all entity
    '''
    return Status.query.get(status)

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    status = Status(**body)
    db.session.add(status)
    db.session.commit()
    return status

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    status = Status.query.get(body['id'])
    if status:
        status = Status(**body)
        db.session.merge(status)
        db.session.flush()
        db.session.commit()
        return status
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    status = Status.query.get(id)
    if status:
        db.session.delete(status)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


