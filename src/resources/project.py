from flask_restful import Resource, reqparse
from flask_jwt import  current_identity
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.project import ProjectModel
from models.user_project_map import UserProjectMap
from models.project_setting_map import ProjectSettingMap


class Project(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type=str,
                      required=True,
                      help="This field cannot be left blank!"
                      )
  parser.add_argument('disabled',
                      type=int,
                      required=False,
                      help="If the project is enabled or not "
                      )

  @jwt_required
  def get(self, id):
    project = ProjectModel.find_by_id(id)
    if project:
      return {'project' : project[0].json() }
    return {'message': 'Item not found'}, 404

  def delete(self, id):
    project = ProjectModel.find_by_id(id)
    if project:
      project.delete_from_db()
      return {'message': 'Item deleted.'}
    return {'message': 'Item not found.'}, 404

  def put(self, id):
    data = Project.parser.parse_args()
    project = ProjectModel.find_by_id(id)
    if project:
      project.name = data['name']
    else:
      project = ProjectModel(None, **data)
    project.save_to_db()
    return project.json()


class ProjectList(Resource):

    @jwt_required
    def get(self):
      return {'projects': list(map(lambda x: x.json(), ProjectModel.get_projects_by_user_id(get_jwt_identity())))}


class NewProject(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type=str,
                      required=True,
                      help="Name of the project"
                      )
  parser.add_argument('disabled',
                      type=int,
                      required=False,
                      default=0,
                      help="If the project is enabled or not "
                      )

  @jwt_required
  def post(self):
    data = NewProject.parser.parse_args()
    user_id = get_jwt_identity()
    check_projects = ProjectModel.get_projects_by_user_id(user_id)
    check_projects = [pr for pr in check_projects if pr.name == data['name']]
    if check_projects:
      return {'message': "A project with name '{}' already exists.".format(data['name'])}, 400

    # Create a new project
    project = ProjectModel(id=None, **data)
    try:
      project.save_to_db()
    except Exception as e:
      print(e)
      return {"message": "An error occurred inserting the item: %s" % repr(e)}, 500

    # Map the project to the user
    mapping_user = UserProjectMap(user_id = user_id, project_id = project.id)
    try:
      mapping_user.save_to_db()
    except Exception as e:
      project.delete_from_db()
      return {"message": "An error occurred mapping the user to the project: %s" % repr(e)}, 500

    return project.json(), 201
