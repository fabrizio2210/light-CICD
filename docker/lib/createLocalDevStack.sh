#!/bin/bash -eu

# Supposing to deploy on x86_64 architecture
docker build -t fabrizio2210/light_cicd-backend-dev -f docker/x86_64/Dockerfile-backend-dev .
docker build -t fabrizio2210/light_cicd-frontend-dev -f docker/x86_64/Dockerfile-frontend-dev .
docker-compose -f docker/lib/stack-dev.yml  up
