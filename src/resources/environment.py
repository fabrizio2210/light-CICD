import copy
import sys
import logging
from flask_restful import Resource, reqparse
from flask_jwt import current_identity
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.environment import EnvironmentModel
from models.project import ProjectModel
from models.project_environment_map import ProjectEnvironmentMap
from models.user_project_map import UserProjectMap


class Environment(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type=str,
                      required=False,
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

  @jwt_required
  def get(self, id):
    envs = EnvironmentModel.find_by_id(id)
    if envs:
      return {'environment': envs[0].json()}
    return {'message': 'Environment not found'}, 404

  @jwt_required
  def delete(self, id):
    # Check the owner
    project_maps = ProjectEnvironmentMap.find_projectmaps_id_by_environment_id(id)
    owner_project_maps = UserProjectMap.find_user_id_by_project_id(project_maps[0].project_id)
    if get_jwt_identity() != owner_project_maps[0].user_id:
      return {'message': "You must be the owner of the project"}, 403

    # Delete from db
    envs = EnvironmentModel.find_by_id(id)
    if envs:
      envs[0].delete_from_db()
      return {'message': 'Environment deleted.'}, 200
    return {'message': 'Environment not found.'}, 404

  @jwt_required
  def put(self, id):
    # Check the owner
    project_maps = ProjectEnvironmentMap.find_projectmaps_id_by_environment_id(id)
    if project_maps:
      owner_project_maps = UserProjectMap.find_user_id_by_project_id(project_maps[0].project_id)
      if get_jwt_identity() != owner_project_maps[0].user_id:
        return {'message': "You must be the owner of the project"}, 403


      # Update the db
      data = Environment.parser.parse_args()
      envs = EnvironmentModel.find_by_id(id)
      if envs:
        env = envs[0]
        project_map = project_maps[0]
        #TODO Can we iterate on the parameters?
        if data.get('name', None) is not None:
          # Check if the environment already exists
          project_env_maps = ProjectEnvironmentMap.find_environment_id_by_project_and_name(project_maps[0].project_id, data['name'])
          if project_env_maps[0].environment_id != env.id:
            return {'message': "A variable with this name for this project already esists"}, 400
          project_map.name = data['name']
          env.name = data['name']
        if data.get('value', None) is not None:
          env.value = data['value']
        if data.get('description', None) is not None:
          env.description = data['description']
        project_map.save_to_db()
        env.save_to_db()
        return {'environment': env.json()}
    return {'message': 'Environment not found.'}, 404


class EnvironmentList(Resource):

  @jwt_required
  def get(self, project_id):
    if len(ProjectModel.find_by_id(project_id)) == 0:
      return {'message': 'Project not found'}, 404
      
    # Check if it is the owner
    project_map = UserProjectMap.find_user_id_by_project_id(project_id)
    if get_jwt_identity() != project_map[0].user_id:
      return {'message': "You must be the owner of the project"}, 403

    return {'environments': list(map(lambda x: x.json(), ProjectEnvironmentMap.get_environments_by_project_id(project_id)))}


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
                      help="Value of the environment variable"
                      )
  parser.add_argument('description',
                      type=str,
                      required=False,
                      help="Description of the environment variable"
                      )

  @jwt_required
  def post(self, project_id):
    projects = ProjectModel.find_by_id(project_id)
    if not projects:
      return {'message': "A project with id '{}' does not exist.".format(project_id)}, 404
    data = NewEnvironment.parser.parse_args()

    # Check if it is the owner
    project_maps = UserProjectMap.find_user_id_by_project_id(project_id)
    if get_jwt_identity() != project_maps[0].user_id:
      return {'message': "You must be the owner of the project"}, 403

    # Check if the environment already exists
    if ProjectEnvironmentMap.find_environment_id_by_project_and_name(project_id, data['name']):
      return {'message': "A variable with this name for this project already esists"}, 400

    # Create a new environment
    env = EnvironmentModel(name=data['name'], id=None, value=data.get('value', None), description=data.get('description', None))
    try:
      env.save_to_db()
    except Exception as e:
      logging.error(e)
      return {"message": "An error occurred inserting the env."}, 500

    # Map the env to the project
    mapping_project = ProjectEnvironmentMap(name = data['name'], project_id = projects[0].id, environment_id = env.id)
    try:
      mapping_project.save_to_db()
    except:
      logging.error(sys.exc_info())
      env.delete_from_db()
      return {"message": "An error occurred mapping the environment to the project."}, 500
    return {'environment': env.json()}, 201
