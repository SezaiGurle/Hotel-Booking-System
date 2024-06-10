from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

# Schedule nightly tasks
app.conf.beat_schedule = {
    'notify-low-capacities': {
        'task': 'tasks.notify_low_capacities',
        'schedule': crontab(hour=0, minute=0),  # Run nightly at midnight
    },
    'process-new-reservations': {
        'task': 'tasks.process_new_reservations',
        'schedule': crontab(hour=0, minute=30),  # Run nightly at 12:30 AM
    },
}
