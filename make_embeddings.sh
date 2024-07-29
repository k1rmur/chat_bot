#!/usr/bin/env bash

git pull && \
docker compose -f embeddings.yml up -d --build