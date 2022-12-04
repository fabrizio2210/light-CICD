from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_jwt import JWT
from flask_cors import CORS
import logging
import os

from db import db
from models.execution import ExecutionModel
from resources.user import UserRegister
from resources.userlogin import UserLogin, TokenRefresh
from resources.project import Project, ProjectList, NewProject
from resources.project_setting import ProjectSetting, ProjectSettingList
from resources.main_setting import MainSettingList, MainSetting
from resources.environment import EnvironmentList, Environment, NewEnvironment
from resources.execution import Execution, NewExecution, ExecutionList, ExecutionOutput
from resources.github import GithubReceiver
from resources.generic_external import GenericExternal
from utils.networking import get_my_ip
from utils.data import bootstrap


if __name__ == '__main__' or os.getenv('DEBUG', 0) == '1':
  logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Initialise from envrironment variables
db.set_db_filename(os.getenv('DB_PATH', '/tmp/data.db'))
ExecutionModel.set_projects_dir(os.getenv('PROJECTS_PATH', '/tmp/projects'))
ExecutionModel.set_projects_volume_string(os.getenv('PROJECTS_VOLUME_STRING', None))
GithubReceiver.set_webhook_secret(os.getenv('WEBHOOK_SECRET', ''))
GenericExternal.set_webhook_secret(os.getenv('GENERIC_WEBHOOK_SECRET', ''))


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_HEADER_TYPE'] = "JWT" 
app.secret_key = os.getenv('JWT_SECRET', 'Qw2sGsa7ED34f6dAfgFSdLopdAdg')
api = Api(app)


# Initialise data
bootstrap(force=False)

# API
jwt = JWTManager(app)
api.add_resource(UserLogin,     '/api/auth')
api.add_resource(TokenRefresh,     '/api/refresh')

api.add_resource(Project,     '/api/v1/project/<int:id>')
api.add_resource(ProjectList, '/api/v1/projects')
api.add_resource(NewProject,  '/api/v1/new_project')

api.add_resource(ProjectSettingList, '/api/v1/project/<int:project_id>/settings')
api.add_resource(ProjectSetting,     '/api/v1/project/<int:project_id>/setting/<string:name>')

api.add_resource(UserRegister, '/api/v1/register')

api.add_resource(MainSetting,     '/api/v1/setting/<string:name>')
api.add_resource(MainSettingList, '/api/v1/settings')

api.add_resource(Environment,     '/api/v1/project/environment/<int:id>')
api.add_resource(EnvironmentList, '/api/v1/project/<int:project_id>/environments')
api.add_resource(NewEnvironment,  '/api/v1/project/<int:project_id>/new_environment')

api.add_resource(ExecutionList, '/api/v1/project/<int:project_id>/executions')
api.add_resource(Execution, '/api/v1/project/<int:project_id>/execution/<int:id>')
api.add_resource(ExecutionOutput, '/api/v1/project/<int:project_id>/execution/<int:id>/output')
api.add_resource(NewExecution, '/api/v1/project/<int:project_id>/new_execution')

api.add_resource(GithubReceiver, '/api/v1/external/github_trigger')
api.add_resource(GenericExternal, '/api/v1/external/generic_trigger')

if __name__ == '__main__':
  logging.info('Started')
  bootstrap(force=True, dev=True)
  from db import db
  my_ip = get_my_ip()
  # enable CORS
  CORS(app, resources={r'/*': {'origins': '*'}})
  logging.info("Connect to http://{}:5000/".format(my_ip))
  app.run(host="0.0.0.0", port=5000, debug=True)
