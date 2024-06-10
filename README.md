# Flask Booking System

This Flask application serves as a booking system with user registration, authentication, and management functionalities. It includes features like hotel management, user roles (admin/non-admin), and integrates with RabbitMQ for asynchronous messaging.

## Key Features

- **User Registration**: Users can register with unique usernames and hashed passwords.
- **User Authentication**: Secure login mechanism with password hashing and JWT-based authentication.
- **Admin Panel**: Admin users have access to an admin dashboard for managing users and hotels.
- **Hotel Management**: CRUD operations for managing hotels, including creation, updating, and deletion.
- **Search Functionality**: Users can search for hotels based on their names.
- **Database Testing**: Includes a utility for testing database connections.

## Security Measures

- **Password Hashing**: User passwords are hashed using the Werkzeug library for secure storage.
- **JWT Authentication**: JSON Web Tokens (JWT) are used for user authentication, ensuring secure access to authorized endpoints.
- **Access Control**: Admin functionalities are restricted to authorized users, preventing unauthorized access.

## Technologies Used

- **Flask**: Web framework for building the application.
- **PostgreSQL**: Database management system for storing user and hotel data.
- **RabbitMQ**: Messaging queue for handling asynchronous tasks.
- **psycopg2**: PostgreSQL adapter for Python.
- **Flask JWT Extended**: Flask extension for JSON Web Token authentication.
- **pika**: Python library for RabbitMQ integration.

## Getting Started

1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`.
3. Set up a PostgreSQL database and RabbitMQ server.
4. Configure database and RabbitMQ connection details in the application.
5. Run the Flask application with `python app.py`.

## Video Link
https://drive.google.com/file/d/1pjhAxU3kQak7Ys3yPlgZkGa3sxo457oX/view?usp=sharing
