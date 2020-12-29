#!/bin/bash

python manage.py makemigrations --noinput && \
python manage.py migrate --noinput && \
python manage.py createsuperuser --noinput --username "admin" --email "admin@edilcloud.it" && \
python manage.py shell < web/management/scripts/import_typology.py && \
python manage.py shell < web/management/scripts/import_category.py || exit 1
# docker exec -i edilcloud-back_web_1 python manage.py shell < web/management/scripts/import_typology.py
# docker exec -i edilcloud-back_web_1 python manage.py shell < web/management/scripts/import_category.py
exec "$@"