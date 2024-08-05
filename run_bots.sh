#!/usr/bin/env bash

git checkout main
git pull && \ 
docker compose -f docker-compose.yml down
docker compose -f docker-compose.yml up -d --build && \
docker network connect protocol_model favr_bot_inner
docker network connect protocol_model favr_bot_outer