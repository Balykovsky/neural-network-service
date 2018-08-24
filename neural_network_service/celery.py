import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neural_network_service.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('neural_network_service')
             # backend="db+postgresql+psycopg2://postgres:postgres@localhost:5432/celery")
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()