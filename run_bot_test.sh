#!/usr/bin/env bash

git pull && \ 
docker compose -f docker-compose_test.yml down
docker compose -f docker-compose_test.yml up -d --build && \
docker network connect protocol_model favr_bot_outer_test