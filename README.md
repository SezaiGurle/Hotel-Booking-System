# Hotel Booking App
 
This code is a Flask application that handles various functionalities such as user registration, session management, database operations, communication with RabbitMQ message queue, etc. Here are the key functions:

register: Creates user registration and sends a message to a RabbitMQ queue after registration is completed.
login: Provides user login functionality. Upon successful login, it redirects the user to either the admin panel if they are an admin or the main page if they are not.
admin_required: Restricts access to a function to only admin users.
admin_dashboard: Displays the admin dashboard.
manage_users: Provides CRUD (Create, Read, Update, Delete) operations for managing users.
manage_hotels: Provides CRUD operations for managing hotels.
search_hotels: Provides hotel search functionality.
hotel_detail: Displays details of a specific hotel.
test_db: Tests the database connection.
Key components of the code include:

It uses psycopg2 for database operations.
Utilizes Flask's built-in session management and Flask JWT Extended for user authentication.
Passwords are hashed using Werkzeug's generate_password_hash and check_password_hash functions.
Uses pika library for asynchronous message queue operations.
The application incorporates important security measures:

Passwords are not stored in plain text in the database; instead, they are hashed.
JWT (JSON Web Token) is used for user authentication.
Access control is enforced for admin functionalities, allowing access only to authorized users.
