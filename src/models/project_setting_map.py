from db import db


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
