import copy
from db import db
from models.init_project_setting import InitProjectSettingModel
from models.setting import SettingModel


class ProjectSettingMap(db.Model):
  project_id = db.Field(_type = "integer")
  setting_id = db.Field(_type = "integer")
  name = db.Field(_type = "string")
  __tablename__ = "project_setting_map"

  def __init__(self, project_id, setting_id, name ):
    self.project_id = project_id
    self.setting_id = setting_id
    self.name = name

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_setting_ids_by_project_id(cls, project_id):
    return cls.find(project_id=project_id)

  @classmethod
  def find_project_id_by_setting_id(cls, setting_id):
    return cls.find(setting_id=setting_id)

  @classmethod
  def find_setting_ids_by_project_id_and_name(cls, project_id, name):
    return cls.find(project_id=project_id, name=name)

  @classmethod
  def get_settings_by_project_id(cls, project_id):
    res = []
    init_settings = InitProjectSettingModel.get_all()
    for init_setting in init_settings:
      res.append(cls.get_project_setting_by_name(project_id, init_setting.name))
    return res

  @classmethod
  def get_project_setting_by_name(cls, project_id, name):
    # find the setting,
    setting = None
    setting_maps = cls.find_setting_ids_by_project_id_and_name(project_id, name)
    if setting_maps:
      settings = SettingModel.find_by_id(setting_maps[0].setting_id)
      setting = settings[0]
    else:
      # if not found, clone by init setting
      init_settings = InitProjectSettingModel.find_by_name(name)
      if not init_settings:
        return None
      settings = SettingModel.find_by_id(init_settings[0].setting_id)
      setting = copy.copy(settings[0])
      setting.id = None
    return setting
