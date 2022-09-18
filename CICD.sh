#!/bin/bash -eux

#############
# Environment

if [ $(uname -m) = "x86_64" ] ; then
  arch="x86_64"
  dockerArch="x86_64"
else
  arch="armv7hf"
  dockerArch="armhf"
fi

################
# Login creation

if [ ! -f ~/.docker/config.json ] ; then 
  mkdir -p ~/.docker/

  if [ -z "$DOCKER_LOGIN" ] ; then
	  echo "Docker login not found in the environment, set DOCKER_LOGIN"
  else
    cat << EOF > ~/.docker/config.json
{
  "experimental": "enabled",
        "auths": {
                "https://index.docker.io/v1/": {
                        "auth": "$DOCKER_LOGIN"
                }
        },
        "HttpHeaders": {
                "User-Agent": "Docker-Client/17.12.1-ce (linux)"
        }
}
EOF
  fi
fi


#######
# Build

docker build -t fabrizio2210/light_cicd-frontend:${arch} -f docker/x86_64/Dockerfile-frontend .
docker build -t fabrizio2210/light_cicd-backend:${arch} -f docker/x86_64/Dockerfile-backend --build-arg DOCKERARCH=${dockerArch} .
docker push fabrizio2210/light_cicd-frontend:${arch}
docker push fabrizio2210/light_cicd-backend:${arch}

#################
# Cleaning Docker

docker container prune --force
docker image prune --force
