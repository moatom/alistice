#! /usr/bin/env bash

# echo "Running inside /app/prestart.sh, you could add migrations to this file, e.g.:"

# echo "
# #! /usr/bin/env bash
# # Let the DB start
# sleep 10;
# # Run migrations
# alembic upgrade head
# "

# sleep 10;
redis-server &
celery -A src.extentions.celery worker --loglevel=info &
# These should be runned when container is made
# flask db init
# flask db migrate
flask db upgrade
uwsgi --ini /app/uwsgi.ini