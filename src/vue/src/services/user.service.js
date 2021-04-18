//import config from 'config';
var config = {};
config.apiUrl = "";

export const userService = {
  login,
  logout,
  refresh
};

function login(username, password) {
  const requestOptions = {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password })
  };

  return fetch(`${config.apiUrl}/api/auth`, requestOptions)
    .then(handleResponse)
    .then(user => {
      // login successful if there's a jwt token in the response
      if (user.access_token) {
        // store user details and jwt token in local storage to keep user logged in between page refreshes
        localStorage.setItem("user", JSON.stringify(user));
      }

      return user;
    });
}

function logout() {
  // remove user from local storage to log user out
  localStorage.removeItem("user");
}

function refresh(refresh_token) {
  const requestOptions = {
    method: "POST",
    headers: new Headers({
      'Authorization': `JWT ${refresh_token}`
    })
  };

  return fetch(`${config.apiUrl}/api/refresh`, requestOptions)
    .then(handleResponse)
    .then(access_token => {
      // login successful if there's a jwt token in the response
      if (access_token) {
        var user = JSON.parse(localStorage.getItem("user"));
        // store user details and jwt token in local storage to keep user logged in between page refreshes
        user.access_token = access_token['access_token'];
        localStorage.setItem("user", JSON.stringify(user));
      }
      return access_token;
    });
}

function handleResponse(response) {
  return response.text().then(text => {
    const data = text && JSON.parse(text);
    if (!response.ok) {
      if (response.status === 401) {
        // auto logout if 401 response returned from api
        logout();
        location.reload(true);
      }

      const error = (data && data.message) || response.statusText;
      return Promise.reject(error);
    }

    return data;
  });
}
