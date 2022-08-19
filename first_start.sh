#!/bin/bash

chmod +x ./run_desarrollo.sh
chmod +x ./run_produccion.sh
chmod +x ./init_db_desarrollo.sh
chmod +x ./env_desarrollo.sh

## Instalar python 3.10
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install -y python3.10 pip

## Instalar postgresql 14
sudo apt -y install gnupg2 wget vim
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt -y update
sudo apt -y install postgresql-14

## Requisitos para psycopg2
# sudo apt install gcc build-essential python-dev python3-dev python3.10-dev musl-dev libssl-dev libldap2-dev libsasl2-dev slapd ldap-utils tox lcov valgrind

sudo apt install -y python3.10-venv
python3.10 -m venv venv

chmod +x ./venv/bin/activate
