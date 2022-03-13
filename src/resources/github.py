
import json
import hmac
import logging
from flask import request
from flask_restful import Resource, reqparse
from models.execution import ExecutionModel
from models.project import ProjectModel
from models.project_setting_map import ProjectSettingMap
from models.setting import SettingModel


class GithubReceiver(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('repository',
                      type=dict,
                      required=True)
  parser.add_argument('X-Hub-Signature-256',
                      location='headers')
  parser.add_argument('X-GitHub-Event',
                      location='headers',
                      required=True)
  hmac = None


  @classmethod
  def set_webhook_secret(cls, secret):
    cls.hmac = hmac.new(bytes(secret, 'utf-8'), digestmod='sha256')


  def post(self):
    data = GithubReceiver.parser.parse_args()
    event = data['X-GitHub-Event']
    repository = data['repository']
    logging.info('Github webhook for: %s', repository['clone_url'])

    hmac_obj = GithubReceiver.hmac.copy()
    hmac_obj.update(request.get_data())
    if not hmac.compare_digest(data['X-Hub-Signature-256'], 'sha256=' + hmac_obj.hexdigest()):
      logging.info('Received X-Hub-Signature-256: %s', data['X-Hub-Signature-256'])
      logging.info('Expected X-Hub-Signature-256: %s', hmac_obj.hexdigest())
      return {'message': 'The X-Hub-Signature-256 is not correct'}, 401
    
    if not 'push' == event:
      return {'message': 'Not handling events different than "push"'}, 400

    settings = SettingModel.find_by_name('scm_url')
    for setting in settings:
      if setting.value == repository['clone_url']:
        project_ids = ProjectSettingMap.find_project_id_by_setting_id(setting.id)
        if not project_ids:
          return {'message': 'Setting is not associate to any project'}, 500
        execution = ExecutionModel(project_id=project_ids[0].project_id)
        try:
          execution.exec()
        except Exception as e:
          logging.error(repr(e))
          return {"message": "An error occurred running the item."}, 500
        return { 'execution': execution.json()}, 201
    return {'message': 'Repository URL not found.'}, 404
        


