#!/usr/bin/env bash

SCRIPT_ABSOLUTE_PATH=$(realpath "$(dirname "${BASH_SOURCE[@]}")")
APP_ABSOLUTE_PATH=$(realpath "$(dirname "$SCRIPT_ABSOLUTE_PATH")")

# export application path to python path
echo "Exporting app path to python path."
export PYTHONPATH=$PYTHONPATH:$APP_ABSOLUTE_PATH

# get postgres credentials
if [ -z "$POSTGRES_USER" ]
then
  echo "No postgres user is provided, please enter a username or 'PG' to default to 'postgres' as the username"
  read -p 'POSTGRES_USER: ' postgres_user_input
  if [ "$postgres_user_input" == "PG" ];
  then
    POSTGRES_USER="postgres"
  else
    POSTGRES_USER="$postgres_user_input"
  fi
fi

if [ -z "$POSTGRES_PASSWORD" ]
then
  echo "No postgres password is provided, please enter a password or 'PASS' to default to 'password' as the postgres password"
  read -sp 'POSTGRES_PASSWORD: ' postgres_password_input
  if [ "$postgres_password_input" == "PASS" ];
  then
    POSTGRES_PASSWORD="postgres"
  else
    POSTGRES_PASSWORD="$postgres_password_input"
  fi
fi

# define database uri
database_uri="postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432"
database="flask_server_side_development"

# kill all application processes that may be accessing db
echo "Killing application processes that may be accessing db .."
set +e
kill -9 $(ps aux | grep '[r]un.py' | awk '{print $2}')

# exit immediately if any none 0 system exits before db operations
set -e
psql "$database_uri" -c ''

# drop and rebuild database
set +e
echo "Dropping the DB ..."
psql "$database_uri" -c "DROP DATABASE IF EXISTS $database"
echo "Rebuilding the DB..."
psql "$database_uri" -c "CREATE DATABASE $database"

# run migrations
cd app || exit
python3 manage.py db upgrade

# seed data
cd ../app/server/data
echo "Seeding system data..."
python3 seed_system_data.py

# start application
cd ../../
python3 run.py
