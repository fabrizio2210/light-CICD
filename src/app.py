from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.project import Project, ProjectList, NewProject
from resources.project_setting import ProjectSettingList
from resources.main_setting import MainSettingList, MainSetting
from resources.environment import EnvironmentList, Environment, NewEnvironment
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

api.add_resource(Project, '/project/<int:id>')
api.add_resource(ProjectSettingList, '/project/<int:project_id>/settings')
api.add_resource(NewProject, '/new_project/<string:name>')
api.add_resource(ProjectList, '/projects')
api.add_resource(UserRegister, '/register')
api.add_resource(MainSetting, '/setting/<int:id>')
api.add_resource(MainSettingList, '/settings')
api.add_resource(EnvironmentList, '/project/<int:project_id>/environments')
api.add_resource(Environment, '/project/environment/<int:id>')
api.add_resource(NewEnvironment, '/project/<int:project_id>/new_environment')

if __name__ == '__main__':
  from db import db
  my_ip = get_my_ip()
  app.run(host=my_ip, port=5000, debug=True)
