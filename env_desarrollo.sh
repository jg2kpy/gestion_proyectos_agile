#!/bin/bash

# Configuracion de Django
export SECRET_KEY="secret"
export DEBUG=1
export DJANGO_ALLOWED_HOSTS="localhost 127.0.0.1"

# Configuracion de DB
export POSTGRES_NAME="postgres"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres"
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
