#!/usr/bin/env bash

git checkout develop
git pull && \ 
docker compose -f docker-compose_test.yml down
docker compose -f docker-compose_test.yml up -d --build && \
docker network connect protocol_model favr_outer_test
