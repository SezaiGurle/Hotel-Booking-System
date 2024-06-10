from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import psycopg2
import pika

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key_here'
jwt = JWTManager(app)

DATABASE = {
    'dbname': 'booking',
    'user': 'sezaigurle',
    'password': 'sezaigurle',
    'host': 'localhost',
    'port': '5432'
}

RABBITMQ_HOST = 'localhost'

def connect_db():
    try:
        conn = psycopg2.connect(**DATABASE)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        raise

def publish_to_rabbitmq(message):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='new_user_queue')
        channel.basic_publish(exchange='', routing_key='new_user_queue', body=message)
    except Exception as e:
        print(f"Failed to publish message to RabbitMQ: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

@app.route('/check_db_connection')
def check_db_connection():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Database connection successful.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin', False))

        hashed_password = generate_password_hash(password)

        try:
            conn = connect_db()
            cur = conn.cursor()

            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Username already exists. Please choose a different username.', 'error')
                return redirect(url_for('register'))

            cur.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)", (username, hashed_password, is_admin))
            conn.commit()

            cur.close()
            conn.close()

            flash('Registration successful. Please log in.', 'success')

            message = f"New user registered: {username}"
            publish_to_rabbitmq(message)

            return redirect(url_for('login'))
        except Exception as e:
            flash(f"An error occurred: {e}", 'error')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            access_token = create_access_token(identity=username)
            session['user_id'] = user[0]
            flash('Login successful.', 'success')

            if user[3]:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('main_page'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        if not user_is_admin(user_id):
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def user_is_admin(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()

    cur.close()
    conn.close()

    return user and user[0]

@app.route('/admin/dashboard')
@jwt_required()
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/admin/users', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_users():
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = bool(request.form.get('is_admin', False))

        if action == 'create':
            hashed_password = generate_password_hash(password)
            cur.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)", (username, hashed_password, is_admin))
        elif action == 'update':
            hashed_password = generate_password_hash(password) if password else None
            if hashed_password:
                cur.execute("UPDATE users SET username = %s, password = %s, is_admin = %s WHERE id = %s", (username, hashed_password, is_admin, user_id))
            else:
                cur.execute("UPDATE users SET username = %s, is_admin = %s WHERE id = %s", (username, is_admin, user_id))
        elif action == 'delete':
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()

    cur.execute("SELECT * FROM users")
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('manage_users.html', users=users)

@app.route('/admin/hotels', methods=['GET', 'POST'])
@jwt_required()
@admin_required
def manage_hotels():
    conn = connect_db()
    cur = conn.cursor()

    if request.method == 'POST':
        action = request.form.get('action')
        hotel_id = request.form.get('hotel_id')
        hotelname = request.form.get('hotelname')
        location = request.form.get('location')
        price = request.form.get('price')

        if action == 'create':
            cur.execute("INSERT INTO hotels (hotelname, location, price) VALUES (%s, %s, %s)", (hotelname, location, price))
        elif action == 'update':
            cur.execute("UPDATE hotels SET hotelname = %s, location = %s, price = %s WHERE id = %s", (hotelname, location, price, hotel_id))
        elif action == 'delete':
            cur.execute("DELETE FROM hotels WHERE id = %s", (hotel_id,))

        conn.commit()

    cur.execute("SELECT * FROM hotels")
    hotels = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('manage_hotels.html', hotels=hotels)

@app.route('/', methods=['GET', 'POST'])
def search_hotels():
    hotels = []
    if request.method == 'POST':
        hotel_name = request.form.get('hotel_name')

        conn = connect_db()
        cur = conn.cursor()

        cur.execute("SELECT * FROM hotels WHERE hotelname ILIKE %s", ('%' + hotel_name + '%',))
        hotels = cur.fetchall()

        cur.close()
        conn.close()
    
    else:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM hotels")
        hotels = cur.fetchall()
        cur.close()
        conn.close()

    return render_template('main_page.html', hotels=hotels)

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    conn = connect_db()
    cur = conn.cursor()
    
    cur.execute("SELECT hotelname, city, capacity, hotel_latitude, hotel_longitude FROM hotels WHERE id = %s", (hotel_id,))
    hotel = cur.fetchone()
    
    hotel_data = {
        'hotel_id': hotel_id,
        'hotel_name': hotel[0],
        'destination': hotel[1],
        'capacity': hotel[2],
        'latitude': hotel[3],
        'longitude': hotel[4]
    }
    
    cur.close()
    conn.close()
    
    return render_template('hotel_detail.html', hotel=hotel_data)

#its connected, its working 
@app.route('/test_db')
def test_db():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Database connection successful.'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
