import copy
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from models.environment import EnvironmentModel
from models.project import ProjectModel
from models.project_environment_map import ProjectEnvironmentMap
from models.user_project_map import UserProjectMap


class Environment(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('value',
                      type=str,
                      required=True,
                      help="This field cannot be left blank!"
                      )

  @jwt_required()
  def get(self, id):
    env = EnvironmentModel.find_by_id(id)
    if env:
      return env[0].json()
    return {'message': 'Environment not found'}, 404

  def delete(self, id):
    env = EnvironmentModel.find_by_id(id)
    project = ProjectEnvironmentMap.find_project_id_by_environment_id(id)
    owner_project = UserProjectMap.find_user_id_by_project_id(project[0].id)
    if current_identity.id != owner_project[0].id:
      return {'message': "You must be the owner of the project"}, 403
    if env:
      env[0].delete_from_db()
      return {'message': 'Environment deleted.'}, 201
    return {'message': 'Environment not found.'}, 404

  def put(self, id):
    data = Project.parser.parse_args()
    project = ProjectModel.find_by_id(id)
    if project:
      project.name = data['name']
    else:
      project = ProjectModel(None, **data)
    project.save_to_db()
    return project.json()


class EnvironmentList(Resource):

  @jwt_required()
  def get(self, project_id):
    if len(ProjectModel.find_by_id(project_id)) == 0:
      return {'message': 'Project not found'}, 404
      
    # Check if it is the owner
    project_map = UserProjectMap.find_user_id_by_project_id(project_id)
    if current_identity.id != project_map[0].user_id:
      return {'message': "You must be the owner of the project"}, 403

    return {'environments': list(map(lambda x: x.json(), EnvironmentModel.get_environments_by_project_id(project_id)))}


class NewEnvironment(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type=str,
                      required=True,
                      help="This field cannot be left blank!"
                      )
  parser.add_argument('value',
                      type=str,
                      required=False,
                      help="This field cannot be left blank!"
                      )
  parser.add_argument('description',
                      type=str,
                      required=False,
                      help="This field cannot be left blank!"
                      )

  @jwt_required()
  def post(self, project_id):
    project = ProjectModel.find_by_id(project_id)
    if not project:
      return {'message': "A project with id '{}' does not exist.".format(project_id)}, 404
    data = NewEnvironment.parser.parse_args()

    # Check if it is the owner
    project_map = UserProjectMap.find_user_id_by_project_id(project_id)
    if current_identity.id != project_map[0].user_id:
      return {'message': "You must be the owner of the project"}, 403

    # Create a new environment
    env = EnvironmentModel(name=data['name'], id=None, value=data.get('value', None), description=data.get('description', None))
    try:
      env.save_to_db()
    except Exception as e:
      print(e)
      return {"message": "An error occurred inserting the env."}, 500

    # Map the env to the project
    mapping_project = ProjectEnvironmentMap(project_id = project[0].id, environment_id = env.id)
    try:
      mapping_project.save_to_db()
    except:
      env.delete_from_db()
      return {"message": "An error occurred mapping the environment to the project."}, 500
    return env.json(), 201
