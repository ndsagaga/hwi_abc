
#!/usr/bin/env python
from models.treatment_task_action import TreatmentTaskAction
from config import db
from werkzeug.exceptions import NotFound

def get():
    '''
    Get all entities
    :returns: all entity
    '''
    return TreatmentTaskAction.query.all()

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    treatment_task_action = TreatmentTaskAction(**body)
    db.session.add(treatment_task_action)
    db.session.commit()
    return treatment_task_action

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    treatment_task_action = TreatmentTaskAction.query.get(body['id'])
    if treatment_task_action:
        treatment_task_action = TreatmentTaskAction(**body)
        db.session.merge(treatment_task_action)
        db.session.flush()
        db.session.commit()
        return treatment_task_action
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    treatment_task_action = TreatmentTaskAction.query.get(id)
    if treatment_task_action:
        db.session.delete(treatment_task_action)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


