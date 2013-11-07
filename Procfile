web: gunicorn wsgi:application
worker: python manage.py rqworker default --settings=settings.prod