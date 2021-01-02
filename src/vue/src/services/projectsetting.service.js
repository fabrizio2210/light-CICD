//import config from 'config';
import { authHeader } from "../helpers";
import { userService } from "./user.service";
var config = {};
config.apiUrl = "";

export const projectsettingService = {
  update,
  getAll
};

function getAll(project_id) {
  const requestOptions = {
    method: "GET",
    headers: authHeader()
  };

  return fetch(`${config.apiUrl}/api/v1/project/${project_id}/settings`, requestOptions).then(
    handleResponse
  );
}

function update(project_id, settingname, settingvalue) {
  const requestOptions = {
    method: "PUT",
    headers: authHeader(),
    body: JSON.stringify({ 'value': settingvalue })
  };

  return fetch(`${config.apiUrl}/api/v1/project/${project_id}/setting/${settingname}`, requestOptions).then(
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
