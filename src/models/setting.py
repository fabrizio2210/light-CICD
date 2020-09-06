from db import db
from models.project_setting_map import ProjectSettingMap


class SettingModel(db.Model):
  id = db.Field(_type = "integer", primary_key =  True)
  name = db.Field(_type = "string")
  description = db.Field(_type = "string")
  default_value = db.Field(_type = "string")
  value = db.Field(_type = "string")
  __tablename__ = "settings"

  def __init__(self, id, name, value = None, description = None, default_value = None):
    if description == None:
      description ="" 
    self.name = name
    self.description = description
    self.default_value = default_value
    self.id = id

  def json(self):
    return {'name': self.name, 'id': self.id, 'description': self.description, 'value': self.value, 'default_value': self.default_value}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def get_settings_by_project_id(cls, project_id):
    res = []
    set_ids = ProjectSettingMap.find_setting_ids_by_project_id(project_id)
    for set_id in set_ids:
      res.append(cls.find_by_id(set_id.setting_id)[0])
    return res

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

  @classmethod
  def find_by_name(cls, name):
    return cls.find(name=name)
