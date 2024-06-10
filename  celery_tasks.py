from celery import Celery
from datetime import datetime, timedelta
import psycopg2

app = Celery('tasks', broker='redis://localhost:6379/0')

# Configuration for the PostgreSQL database
DATABASE = {
    'dbname': 'booking',
    'user': 'sezaigurle',
    'password': 'sezaigurle',
    'host': 'localhost'
}

def connect_db():
    return psycopg2.connect(**DATABASE)

@app.task
def notify_low_capacities():
    conn = connect_db()
    cur = conn.cursor()

    # Get the date for next month
    next_month = datetime.now() + timedelta(days=30)

    # Query hotels with capacity below 20% for next month
    query = """
        SELECT hotel_name, capacity 
        FROM hotels 
        WHERE capacity < 0.2 * capacity AND start_date >= %s
    """
    cur.execute(query, (next_month,))
    low_capacity_hotels = cur.fetchall()

    cur.close()
    conn.close()

    # Send notifications to hotel administrators
    for hotel in low_capacity_hotels:
        # Send notification email, SMS, or any other preferred method
        pass

@app.task
def process_new_reservations():
    # Logic to pull new reservations from the queue and send messages to users
    pass
