from db import db


class ProjectSettingMap(db.Model):
  project_id = db.Field(_type = "integer")
  setting_id = db.Field(_type = "integer")
  __tablename__ = "project_setting_map"

  def __init__(self, project_id, setting_id ):
    self.project_id = project_id
    self.setting_id = setting_id

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_setting_ids_by_project_id(cls, project_id):
    return cls.find(project_id=project_id)
