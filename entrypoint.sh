#!/bin/sh

./wait-for-it.sh mariadb:3306 --timeout=60 --strict -- echo "MariaDB is up"

python manage.py makemigrations

python manage.py migrate

python manage.py runserver 0.0.0.0:8000