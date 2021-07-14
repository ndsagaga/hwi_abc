
#!/usr/bin/env python
from models.treatment_task import TreatmentTask
from config import db
from werkzeug.exceptions import NotFound

def get():
    '''
    Get all entities
    :returns: all entity
    '''
    return TreatmentTask.query.all()

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    treatment_task = TreatmentTask(**body)
    db.session.add(treatment_task)
    db.session.commit()
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
        db.session.commit()
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
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


