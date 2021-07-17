
#!/usr/bin/env python
from os import stat
from models.treatment_task import TreatmentTask
from config import db
from werkzeug.exceptions import NotFound

def get(task_id):
    '''
    Get all entities
    :returns: all entity
    '''
    return TreatmentTask.query.get(task_id)

def getForDogAndStatus(tag, status):
    '''
    Get all entities
    :returns: all entity
    '''
    return TreatmentTask.query.filter_by(tag=tag, status=status).all()

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    treatment_task = TreatmentTask(**body)
    db.session.add(treatment_task)
    return treatment_task

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    treatment_task = TreatmentTask.query.get(body['id'])
    if treatment_task:
        treatment_task = TreatmentTask(**body)
        db.session.merge(treatment_task)
        db.session.flush()
        return treatment_task
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    treatment_task = TreatmentTask.query.get(id)
    if treatment_task:
        db.session.delete(treatment_task)
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


