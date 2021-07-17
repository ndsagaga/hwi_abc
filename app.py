#!/usr/bin/env python
from config import app
from config import db
from controllers.user_controller import api as user_api
from controllers.dog_controller import api as dog_api
from controllers.dog_status_controller import api as dog_status_api
from controllers.treatment_task_controller import api as treatment_task_api
from controllers.treatment_task_action_controller import api as treatment_task_action_api

# register the api
app.register_blueprint(user_api)
app.register_blueprint(dog_api)
app.register_blueprint(dog_status_api)
app.register_blueprint(treatment_task_api)
app.register_blueprint(treatment_task_action_api)

if __name__ == '__main__':
    ''' run application '''
    print(db)
    app.run(host='0.0.0.0', port=5000)
