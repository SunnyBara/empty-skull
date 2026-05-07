

#!/bin/sh

echo "Starting app..."

python manage.py migrate
python manage.py collectstatic --noinput

exec "$@"