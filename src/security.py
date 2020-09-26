from werkzeug.security import safe_str_cmp
from models.user import UserModel


def authenticate(username, password):
    users = UserModel.find_by_username(username)
    if users and safe_str_cmp(users[0].password, password):
        return users[0]


def identity(payload):
    user_id = payload['identity']
    users = UserModel.find_by_id(user_id)
    if users:
      return users[0]
    return None
