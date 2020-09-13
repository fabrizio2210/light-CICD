import copy
from db import db


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
    self.value = value
    self.id = id

  def json(self):
    return {'name': self.name, 'id': self.id, 'description': self.description, 'value': self.value, 'default_value': self.default_value}

  def save_to_db(self):
    self.save()

  def delete_from_db(self):
    self.delete()

  @classmethod
  def find_by_id(cls, id):
    return cls.find(id=id)

