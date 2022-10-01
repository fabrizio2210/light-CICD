//import config from 'config';
import { authHeader } from "../helpers";
import { userService } from "./user.service";
var config = {};
config.apiUrl = "";

export const executionService = {
  del,
  get,
  exec,
  getAll
};

function getAll(project_id) {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(
    `${config.apiUrl}/api/v1/project/${project_id}/executions`,
    requestOptions
  ).then(handleResponse);
}

function exec(project_id) {
  const requestOptions = {
    method: "POST",
    headers: authHeader()
  };

  return fetch(
    `${config.apiUrl}/api/v1/project/${project_id}/new_execution`,
    requestOptions
  ).then(handleResponse);
}

function get(project_id, execution_id) {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(
    `${config.apiUrl}/api/v1/project/${project_id}/execution/${execution_id}`,
    requestOptions
  ).then(handleResponse);
}

function del(project_id, execution_id) {
  const requestOptions = {
    method: "DELETE",
    headers: authHeader()
  };

  return fetch(
    `${config.apiUrl}/api/v1/project/${project_id}/execution/${execution_id}`,
    requestOptions
  ).then(handleResponse);
}

function handleResponse(response) {
  return response.text().then(text => {
    const data = text && JSON.parse(text);
    if (!response.ok) {
      if (response.status === 401) {
        // auto logout if 401 response returned from api
        userService.logout();
        location.reload(true);
      }

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }

    return data;
  });
}
