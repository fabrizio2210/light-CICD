import copy
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from models.setting import SettingModel
from models.project import ProjectModel
from models.project_setting_map import ProjectSettingMap


class ProjectSetting(Resource):
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

  def post(self):
    pass

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


class ProjectSettingList(Resource):

    @jwt_required()
    def get(self, project_id):
      if len(ProjectModel.find_by_id(project_id)) == 0:
        return {'message': 'Project not found'}, 404
      return {'settings': list(map(lambda x: x.json(), SettingModel.get_settings_by_project_id(project_id)))}


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

    # Create new settings from initial ones
    init_settings = InitProjectSettingModel.get_all_settings()
    done_settings = []
    done_setting_mappings = []
    for init_setting in init_settings:
      new_setting = copy.copy(init_setting)
      new_setting.id = None
      try:
        new_setting.save_to_db()
      except:
        project.delete_from_db()
        mapping_user.delete_from_db()
        for setting in done_settings:
          setting.delete_from_db()
        for setting_map in done_setting_mappings:
          setting_map.delete_from_db()
      done_settings.append(new_setting)

      # Associate the setting to the project
      mapping_setting = ProjectSettingMap(project_id=project.id, setting_id=new_setting.id)
      try:
        mapping_setting.save()
      except:
        project.delete_from_db()
        mapping_user.delete_from_db()
        for setting in done_settings:
          setting.delete_from_db()
        for setting_map in done_setting_mappings:
          setting_map.delete_from_db()
        return {"message": "An error occurred mapping the settins to the project."}, 500
        done_setting_mappings.append(mapping_setting)


    return project.json(), 201
