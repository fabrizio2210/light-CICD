//import config from 'config';
import { authHeader } from "../helpers";
import { userService } from "./user.service";
var config = {};
config.apiUrl = "";

export const projectService = {
  create,
  get,
  getAll
};

function getAll() {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(`${config.apiUrl}/api/v1/projects`, requestOptions).then(
    handleResponse
  );
}

function get(project_id) {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(
    `${config.apiUrl}/api/v1/project/${project_id}`,
    requestOptions
  ).then(handleResponse);
}

function create(projectname) {
  const requestOptions = {
    method: "POST",
    headers: authHeader(),
    body: JSON.stringify({ name: projectname })
  };

  return fetch(`${config.apiUrl}/api/v1/new_project`, requestOptions).then(
    handleResponse
  );
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
