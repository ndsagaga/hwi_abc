def func(inp):
    inparr = inp.split()
    col = inparr[0].replace('`','')
    if ('VARCHAR' in inparr[1]):
        return "<COL> = db.Column(db.String(255), nullable=True)".replace('<COL>',col)
    if ('INT' in inparr[1]):
        return "<COL> = db.Column(db.Integer(), nullable=True)".replace('<COL>',col)
    if ('FLOAT' in inparr[1]):
        return "<COL> = db.Column(db.Float(), nullable=True)".replace('<COL>',col)
    if ('BOOLEAN' in inparr[1]):
        return "<COL> = db.Column(db.Boolean(), nullable=True)".replace('<COL>',col)
    if ('TIMESTAMP' in inparr[1]):
        return "<COL> = db.Column(db.Timestamp(), nullable=True)".replace('<COL>',col)
    if ('TEXT' in inparr[1]):
        return "<COL> = db.Column(db.Text(), nullable=True)".replace('<COL>',col)

s = """
#!/usr/bin/env python
from models.<LOWER> import <CAPITALIZED>
from config import db
from werkzeug.exceptions import NotFound

def get():
    '''
    Get all entities
    :returns: all entity
    '''
    return <CAPITALIZED>.query.all()

def post(body):
    '''
    Create entity with body
    :param body: request body
    :returns: the created entity
    '''
    <LOWER> = <CAPITALIZED>(**body)
    db.session.add(<LOWER>)
    db.session.commit()
    return <LOWER>

def put(body):
    '''
    Update entity by id
    :param body: request body
    :returns: the updated entity
    '''
    <LOWER> = <CAPITALIZED>.query.get(body['id'])
    if <LOWER>:
        <LOWER> = <CAPITALIZED>(**body)
        db.session.merge(<LOWER>)
        db.session.flush()
        db.session.commit()
        return <LOWER>
    raise NotFound('no such entity found with id=' + str(body['id']))

def delete(id):
    '''
    Delete entity by id
    :param id: the entity id
    :returns: the response
    '''
    <LOWER> = <CAPITALIZED>.query.get(id)
    if <LOWER>:
        db.session.delete(<LOWER>)
        db.session.commit()
        return {'success': True}
    raise NotFound('no such entity found with id=' + str(id))


"""

#for l in s.splitlines():
#    print(func(l))

for obj in [['dog_status', 'DogStatus'], ['dog','Dog'], ['role', 'Role'], ['status', 'Status'], ['treatment_task_action', 'TreatmentTaskAction'], ['treatment_task', 'TreatmentTask'],['user_session','UserSession']]:
    with open('services/'+obj[0]+'_service.py', 'w') as f:
            f.write(s.replace('<LOWER>',obj[0]).replace('<CAPITALIZED>',obj[1]))

