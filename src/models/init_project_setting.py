from db import db
from models.setting import SettingModel


class InitProjectSettingModel(db.Model):
  name = db.Field(_type = "string", primary_key =  True)
  setting_id = db.Field(_type = "integer")
  __tablename__ = "init_project_settings"

  def __init__(self, name , setting_id ):
    self.name = name
    self.setting_id = setting_id

  def json(self):
    return {'name': self.name, 'setting_id': self.setting_id}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def get_all(cls):
    return cls.find()

  @classmethod
  def get_all_settings(cls):
    res = []
    m_settings = cls.get_all()
    for m_setting in m_settings:
      res.append(SettingModel.find_by_id(m_setting.setting_id)[0])
    return res

  @classmethod
  def get_setting_by_name(cls, name):
    res = []
    m_settings = cls.find_by_name(name)
    for m_setting in m_settings:
      res.append(SettingModel.find_by_id(m_setting.setting_id)[0])
    return res

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

  @classmethod
  def find_by_name(cls, name):
    return cls.find(name=name)
