from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_jwt import JWT
from flask_cors import CORS
import logging

from resources import frontend
from resources.user import UserRegister
from resources.userlogin import UserLogin, TokenRefresh
from resources.project import Project, ProjectList, NewProject
from resources.project_setting import ProjectSetting, ProjectSettingList
from resources.main_setting import MainSettingList, MainSetting
from resources.environment import EnvironmentList, Environment, NewEnvironment
from resources.execution import Execution, NewExecution, ExecutionList, ExecutionOutput
from utils.networking import get_my_ip
from utils.data import bootstrap


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_HEADER_TYPE'] = "JWT" 
app.secret_key = 'jose'
api = Api(app)



# API
jwt = JWTManager(app)
api.add_resource(UserLogin,     '/api/auth')
api.add_resource(TokenRefresh,     '/api/refresh')

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

api.add_resource(ExecutionList, '/api/v1/project/<int:project_id>/executions')
api.add_resource(Execution, '/api/v1/project/<int:project_id>/execution/<int:id>')
api.add_resource(ExecutionOutput, '/api/v1/project/<int:project_id>/execution/<int:id>/output')
api.add_resource(NewExecution, '/api/v1/project/<int:project_id>/new_execution')

# Frontend
app.add_url_rule('/', view_func=frontend.index)
app.add_url_rule('/web/login/', view_func=frontend.login)
app.add_url_rule('/web/projects/', view_func=frontend.projects)
app.add_url_rule('/css/stylesheet.css', view_func=frontend.stylesheet)
app.add_url_rule('/js/main.js', view_func=frontend.main_js)
app.add_url_rule('/js/projects.js', view_func=frontend.projects_js)

if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
  logging.info('Started')
  bootstrap()
  from db import db
  my_ip = get_my_ip()
  # enable CORS
  CORS(app, resources={r'/*': {'origins': '*'}})
  logging.info("Connect to http://{}:5000/".format(my_ip))
  app.run(host="0.0.0.0", port=5000, debug=True)
