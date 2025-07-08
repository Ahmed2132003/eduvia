web: gunicorn Eduvia.wsgi:application --bind 0.0.0.0:8000 --log-file -
worker: celery -A Eduvia worker --loglevel=info
beat: celery -A Eduvia beat --loglevel=info