from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
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

  @jwt_required()
  def get(self, name):
    project = ProjectModel.find_by_name(name)
    if project:
      return project[0].json()
    return {'message': 'Item not found'}, 404

  @jwt_required()
  def get(self, id):
    project = ProjectModel.find_by_id(id)
    if project:
      return project[0].json()
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

    @jwt_required()
    def get(self):
      return {'projects': list(map(lambda x: x.json(), ProjectModel.get_projects_by_user_id(current_identity.id)))}


class NewProject(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('disabled',
                      type=int,
                      required=False,
                      default=0,
                      help="If the project is enabled or not "
                      )

  @jwt_required()
  def post(self, name):
    if ProjectModel.find_by_name(name):
      return {'message': "A project with name '{}' already exists.".format(name)}, 400
    data = NewProject.parser.parse_args()

    # Create a new project
    project = ProjectModel(name=name, id=None, **data)
    try:
      project.save_to_db()
    except Exception as e:
      print(e)
      return {"message": "An error occurred inserting the item."}, 500

    # Map the project to the user
    mapping_user = UserProjectMap(user_id = current_identity.id, project_id = project.id)
    try:
      mapping_user.save_to_db()
    except:
      project.delete_from_db()
      return {"message": "An error occurred mapping the user to the project."}, 500

    return project.json(), 201
