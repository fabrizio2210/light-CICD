
import json
import hmac
import logging
from flask import request
from flask_restful import Resource, reqparse
from models.execution import ExecutionModel
from models.project import ProjectModel
from models.project_setting_map import ProjectSettingMap
from models.environment import EnvironmentModel
from models.setting import SettingModel


class GenericExternal(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('repository',
                      type=str,
                      required=True)
  parser.add_argument('Signature-256',
                      location='headers',
                      required=True)
  parser.add_argument('envs',
                      location='json',
                      type=list,
                      required=False)
  hmac = None


  @classmethod
  def set_webhook_secret(cls, secret):
    cls.hmac = hmac.new(bytes(secret, 'utf-8'), digestmod='sha256')


  def post(self):
    data = GenericExternal.parser.parse_args()
    repository = data['repository']
    logging.info('Generic External webhook for: %s', repository)

    hmac_obj = GenericExternal.hmac.copy()
    hmac_obj.update(request.get_data())
    if not hmac.compare_digest(data['Signature-256'], 'sha256=' + hmac_obj.hexdigest()):
      logging.info('Received Signature-256: %s', data['Signature-256'])
      logging.info('Expected Signature-256: %s', hmac_obj.hexdigest())
      return {'message': 'The Signature-256 is not correct'}, 401
    
    data_envs = data['envs']
    envs = []
    for env_string in data_envs:
      parts = env_string.split("=")
      if len(parts) > 2:
        env = EnvironmentModel(parts[0], parts[0], parts[1])
        envs.append(env)
      else:
        logging.info("Ignored the following string because without '=' %s", env_string)

    settings = SettingModel.find_by_name('scm_url')
    for setting in settings:
      if setting.value == repository:
        project_ids = ProjectSettingMap.find_project_id_by_setting_id(setting.id)
        if not project_ids:
          return {'message': 'Setting is not associate to any project'}, 500
        execution = ExecutionModel(project_id=project_ids[0].project_id)
        try:
          execution.exec(supplement_envs=envs)
        except Exception as e:
          logging.error(repr(e))
          return {"message": "An error occurred running the item: %s" % repr(e)}, 500
        return { 'execution': execution.json()}, 201
    return {'message': 'Repository URL not found.'}, 404
        


