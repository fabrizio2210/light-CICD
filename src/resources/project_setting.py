import copy
from flask_restful import Resource, reqparse
from flask_jwt import jwt_required, current_identity
from models.setting import SettingModel
from models.project import ProjectModel
from models.project_setting_map import ProjectSettingMap
from models.user_project_map import UserProjectMap


class ProjectSetting(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('value',
                      type=str,
                      required=True,
                      help="This field cannot be left blank!"
                      )

  @jwt_required()
  def get(self, project_id, name):
    # Check if project owner
    owner_maps = UserProjectMap.find_user_id_by_project_id(project_id)
    if not owner_maps:
      return {'message': "Project not found"}, 404
    if owner_maps[0].user_id != current_identity.id:
      return {'message': "You have to own the project"}, 403

    # find the setting,
    setting = None
    setting_maps = ProjectSettingMap.find_setting_ids_by_project_id_and_name(project_id, name)
    if setting_maps:
      settings = SettingModel.find_by_id(setting_maps[0].setting_id)
      setting = settings[0]
    else:
      # if not found, clone by init setting
      init_settings = InitProjectSettingModel.find_by_name(name)
      if not init_settings:
        return {'message': "The name of the setting does not exist"}, 400
      settings = SettingModel.find_by_id(init_settings[0].setting_id)
      setting = copy.copy(settings[0])
      setting.id = None

    return setting.json()

  @jwt_required()
  def put(self, project_id, name):
    # Check if project owner
    owner_maps = UserProjectMap.find_user_id_by_project_id(project_id)
    if not owner_maps:
      return {'message': "Project not found"}, 404
    if owner_maps[0].user_id != current_identity.id:
      return {'message': "You have to own the project"}, 403

    # find the setting,
    setting = None
    setting_maps = ProjectSettingMap.find_setting_ids_by_project_id_and_name(project_id, name)
    if setting_maps:
      settings = SettingModel.find_by_id(setting_maps[0].setting_id)
      setting = settings[0]
    else:
      # if not found, clone by init setting
      init_settings = InitProjectSettingModel.find_by_name(name)
      if not init_settings:
        return {'message': "The name of the setting does not exist"}, 400
      settings = SettingModel.find_by_id(init_settings[0].setting_id)
      setting = copy.copy(settings[0])
      setting.id = None

    # Update fields
    data = ProjectSetting.parser.parse_args()
    setting.value = data['value']
    try:
      setting.save_to_db()
    except:
      return {'message': "An error occurred creating the setting"}, 500

    # Associate setting to the project, if new
    if not setting_maps:
      mapping_setting = ProjectSettingMap(project_id=project_id, setting_id=setting.id, name=setting.name)
      try:
        mapping_setting.save()
      except:
        setting.delete_from_db()
        return {'message': "An error occurred mapping the setting to the project"}, 500

    return setting.json()


class ProjectSettingList(Resource):

    @jwt_required()
    def get(self, project_id):
      if len(ProjectModel.find_by_id(project_id)) == 0:
        return {'message': 'Project not found'}, 404
      return {'settings': list(map(lambda x: x.json(), SettingModel.get_settings_by_project_id(project_id)))}


