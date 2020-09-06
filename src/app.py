from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.project import Project, ProjectList, NewProject
from utils.networking import get_my_ip


app = Flask(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'jose'
api = Api(app)


@app.before_first_request
def create_tables():
  from models.user import UserModel
  from models.user_project_map import UserProjectMap
  from models.project import ProjectModel
  UserModel.create_table()
  UserProjectMap.create_table()
  ProjectModel.create_table()
  new_user = UserModel(id=None, username="fabrizio", password="pwd", admin=1)
  new_user.save()
  new_user = UserModel(id=None, username="fabrizio2", password="pwd2", admin=0)
  new_user.save()
  print(UserModel.find_by_username("jose"))
  print(UserModel.find_by_id(1))
  print(UserModel.find_by_username("fabrizio"))
  print(UserModel.get_all())
  
  


jwt = JWT(app, authenticate, identity)  # /auth

api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(Project, '/project/<int:id>')
api.add_resource(NewProject, '/new_project/<string:name>')
api.add_resource(ProjectList, '/projects')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
  from db import db
  my_ip = get_my_ip()
  app.run(host=my_ip, port=5000, debug=True)
