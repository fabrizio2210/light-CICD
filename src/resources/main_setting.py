from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.main_setting import MainSettingModel
from models.user import UserModel


class MainSetting(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('value',
                      type=str,
                      required=True,
                      help="This field cannot be left blank!"
                      )

  @jwt_required
  def get(self, name):
    settings = MainSettingModel.get_setting_by_name(name)
    if settings:
      return settings[0].json()
    return {'message': 'Item not found'}, 404

  @jwt_required
  def put(self, name):
    data = MainSetting.parser.parse_args()
    users = UserModel.find_by_id(get_jwt_identity())
    if users[0].admin != 1:
      return {'message': "Admin privileges are required"}, 403
    settings = MainSettingModel.get_setting_by_name(name)
    if settings:
      settings[0].value = data['value']
    else:
      return {'message': "Setting not found"}, 404
    settings[0].save_to_db()
    return settings[0].json()


class MainSettingList(Resource):

    @jwt_required
    def get(self):
      return {'settings': list(map(lambda x: x.json(), MainSettingModel.get_all_settings()))}


