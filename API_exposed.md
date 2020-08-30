# API

## Frontend API

### /web/login

Login web page, it is necessary to retrieve a security token 

### /web/settings (secured)

Page where manipulate the overall settings

### /web/projects (secured)

Page of all projects

### /web/projects/<id_project>/ (secured)

Page of the project identified by id_project

### /web/projects/<id_project>/settings (secured)

Page where change the settings of the id_project project



## Backend API


### /api/v1/projects/ (secured)

List of all projects

### /api/v1/projects/<id_project>/ (secured)

All details of the project identified by id_project

### /api/v1/projects/<id_project>/settings GET/POST (secured)

Retrieve and set the settings of the id_project project

### /api/v1/projects/<id_project>/builds (secured)

All the builds of the id_project project

### /api/v1/projects/<id_project>/build POST (secured)

Trigger a build of the project id_project
