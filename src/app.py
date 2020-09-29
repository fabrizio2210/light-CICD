from flask import Flask
from flask_restful import Api
from flask_jwt import JWT
import logging

from security import authenticate, identity
from resources.user import UserRegister
from resources.project import Project, ProjectList, NewProject
from resources.project_setting import ProjectSetting, ProjectSettingList
from resources.main_setting import MainSettingList, MainSetting
from resources.environment import EnvironmentList, Environment, NewEnvironment
from resources.execution import Execution, NewExecution
from utils.networking import get_my_ip
from utils.data import bootstrap


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jose'
api = Api(app)


@app.before_first_request
def initialization():
  bootstrap()


jwt = JWT(app, authenticate, identity)  # /auth

api.add_resource(Project,     '/api/v1/project/<int:id>')
api.add_resource(ProjectList, '/api/v1/projects')
api.add_resource(NewProject,  '/api/v1/new_project/<string:name>')

api.add_resource(ProjectSettingList, '/api/v1/project/<int:project_id>/settings')
api.add_resource(ProjectSetting,     '/api/v1/project/<int:project_id>/setting/<string:name>')

api.add_resource(UserRegister, '/api/v1/register')

api.add_resource(MainSetting,     '/api/v1/setting/<string:name>')
api.add_resource(MainSettingList, '/api/v1/settings')

api.add_resource(Environment,     '/api/v1/project/environment/<int:id>')
api.add_resource(EnvironmentList, '/api/v1/project/<int:project_id>/environments')
api.add_resource(NewEnvironment,  '/api/v1/project/<int:project_id>/new_environment')

api.add_resource(NewExecution, '/api/v1/project/<int:project_id>/build')

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO)
  logging.info('Started')
  from db import db
  my_ip = get_my_ip()
  app.run(host=my_ip, port=5000, debug=True)
