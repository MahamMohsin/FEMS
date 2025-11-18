# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from flask_login import UserMixin
# from dotenv import load_dotenv
# import os
# import bcrypt
# import jwt
# from datetime import datetime, timedelta
# from functools import wraps

# # Load environment variables from .env file
# load_dotenv()

# # Initialize Flask app
# app = Flask(__name__)

# # Enable CORS - This allows your React frontend to communicate with Flask backend
# # Without this, browsers block requests between different ports (CORS policy)
# CORS(app)

# # Configure database connection
# # SQLAlchemy will use this URL to connect to your Supabase PostgreSQL database
# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable unnecessary feature
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Used for JWT token signing

# # Create database instance - this object handles all database operations
# db = SQLAlchemy(app)


# # ============================================================================
# # DATABASE MODEL - Define the User table structure
# # ============================================================================
# class User(db.Model, UserMixin):
#     """
#     User model represents the 'users' table in database
#     Each attribute below becomes a column in the table
#     """
#     __tablename__ = 'users'  # Name of the table in database

#     # Primary key - unique identifier for each user
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
#     # Email - must be unique, cannot be empty
#     email = db.Column(db.String(320), unique=True, nullable=False)
    
#     # Password hash - we NEVER store plain passwords, only hashed versions
#     password_hash = db.Column(db.String(255), nullable=False)
    
#     # Role - either 'student' or 'vendor'
#     role = db.Column(db.String(20), nullable=False)
    
#     # Full name of the user
#     full_name = db.Column(db.String(200), nullable=False)
    
#     # Phone number
#     phone = db.Column(db.String(20), nullable=False)
    
#     # Timestamp when account was created
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
#     # Last login timestamp - can be empty initially
#     last_login = db.Column(db.DateTime, nullable=True)

#     def __repr__(self):
#         """String representation of User object - useful for debugging"""
#         return f'<User {self.email}>'


# # ============================================================================
# # AUTHENTICATION DECORATOR - Protect routes that need login
# # ============================================================================
# def token_required(f):
#     """
#     This is a decorator function that checks if user is logged in
#     It verifies the JWT token sent in request headers
#     Use @token_required above any route that needs authentication
#     """
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
        
#         # Check if token is present in request headers
#         # Format: Authorization: Bearer <token>
#         if 'Authorization' in request.headers:
#             try:
#                 # Extract token from "Bearer <token>" format
#                 token = request.headers['Authorization'].split(" ")[1]
#             except IndexError:
#                 return jsonify({'error': 'Invalid token format'}), 401
        
#         # If no token found, user is not logged in
#         if not token:
#             return jsonify({'error': 'Token is missing'}), 401
        
#         try:
#             # Verify and decode the token using secret key
#             data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
#             # Get user from database using ID stored in token
#             current_user = User.query.filter_by(id=data['user_id']).first()
            
#             if not current_user:
#                 return jsonify({'error': 'User not found'}), 401
                
#         except jwt.ExpiredSignatureError:
#             # Token has expired (older than 7 days)
#             return jsonify({'error': 'Token has expired'}), 401
#         except jwt.InvalidTokenError:
#             # Token is invalid or tampered with
#             return jsonify({'error': 'Invalid token'}), 401
        
#         # Pass the current user to the route function
#         return f(current_user, *args, **kwargs)
    
#     return decorated


# # ============================================================================
# # API ROUTES - Endpoints that handle requests
# # ============================================================================

# @app.route('/')
# def home():
#     """
#     Root endpoint - just confirms the server is running
#     Test by visiting: http://localhost:5000/
#     """
#     return jsonify({
#         'message': 'FEMS Backend API is running!',
#         'version': '1.0',
#         'endpoints': {
#             'register': '/api/register',
#             'login': '/api/login',
#             'profile': '/api/profile'
#         }
#     })


# @app.route('/api/register', methods=['POST'])
# def register():
#     """
#     Register a new user
#     Expected JSON format:
#     {
#         "email": "student@example.com",
#         "password": "securepassword123",
#         "full_name": "John Doe",
#         "phone": "03001234567",
#         "role": "student"  // or "vendor"
#     }
#     """
#     try:
#         # Get JSON data from request body
#         data = request.get_json()
        
#         # Validate required fields
#         required_fields = ['email', 'password', 'full_name', 'phone', 'role']
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({'error': f'{field} is required'}), 400
        
#         # Extract data
#         email = data['email'].lower().strip()  # Convert to lowercase and remove spaces
#         password = data['password']
#         full_name = data['full_name'].strip()
#         phone = data['phone'].strip()
#         role = data['role'].lower()
        
#         # Validate role
#         if role not in ['student', 'vendor']:
#             return jsonify({'error': 'Role must be either student or vendor'}), 400
        
#         # Validate password length
#         if len(password) < 6:
#             return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
#         # Check if user already exists
#         existing_user = User.query.filter_by(email=email).first()
#         if existing_user:
#             return jsonify({'error': 'Email already registered'}), 409
        
#         # Hash the password using bcrypt
#         # This converts "password123" into something like "$2b$12$KIX..."
#         # Even if database is hacked, attackers can't get original passwords
#         password_bytes = password.encode('utf-8')  # Convert string to bytes
#         salt = bcrypt.gensalt()  # Generate random salt
#         hashed_password = bcrypt.hashpw(password_bytes, salt)  # Hash with salt
        
#         # Create new user object
#         new_user = User(
#             email=email,
#             password_hash=hashed_password.decode('utf-8'),  # Store as string
#             full_name=full_name,
#             phone=phone,
#             role=role
#         )
        
#         # Add to database
#         db.session.add(new_user)
#         db.session.commit()
        
#         return jsonify({
#             'message': 'User registered successfully!',
#             'user': {
#                 'id': new_user.id,
#                 'email': new_user.email,
#                 'full_name': new_user.full_name,
#                 'role': new_user.role
#             }
#         }), 201
        
#     except Exception as e:
#         # If anything goes wrong, rollback database changes
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/login', methods=['POST'])
# def login():
#     """
#     Login user and return JWT token
#     Expected JSON format:
#     {
#         "email": "student@example.com",
#         "password": "securepassword123"
#     }
#     """
#     try:
#         # Get JSON data
#         data = request.get_json()
        
#         # Validate required fields
#         if 'email' not in data or 'password' not in data:
#             return jsonify({'error': 'Email and password are required'}), 400
        
#         email = data['email'].lower().strip()
#         password = data['password']
        
#         # Find user in database
#         user = User.query.filter_by(email=email).first()
        
#         # Check if user exists
#         if not user:
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         # Verify password
#         # bcrypt.checkpw compares the provided password with stored hash
#         password_bytes = password.encode('utf-8')
#         stored_hash = user.password_hash.encode('utf-8')
        
#         if not bcrypt.checkpw(password_bytes, stored_hash):
#             return jsonify({'error': 'Invalid email or password'}), 401
        
#         # Update last login time
#         user.last_login = datetime.utcnow()
#         db.session.commit()
        
#         # Generate JWT token
#         # This token acts like a ticket that proves the user is logged in
#         # It contains user_id and role, and expires after 7 days
#         token_payload = {
#             'user_id': user.id,
#             'role': user.role,
#             'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
#         }
        
#         token = jwt.encode(
#             token_payload,
#             app.config['SECRET_KEY'],
#             algorithm='HS256'
#         )
        
#         return jsonify({
#             'message': 'Login successful!',
#             'token': token,
#             'user': {
#                 'id': user.id,
#                 'email': user.email,
#                 'full_name': user.full_name,
#                 'role': user.role
#             }
#         }), 200
        
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# @app.route('/api/profile', methods=['GET'])
# @token_required  # This route requires authentication
# def get_profile(current_user):
#     """
#     Get logged-in user's profile
#     Requires: Authorization header with Bearer token
#     Example: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
#     """
#     return jsonify({
#         'user': {
#             'id': current_user.id,
#             'email': current_user.email,
#             'full_name': current_user.full_name,
#             'phone': current_user.phone,
#             'role': current_user.role,
#             'created_at': current_user.created_at.isoformat(),
#             'last_login': current_user.last_login.isoformat() if current_user.last_login else None
#         }
#     }), 200


# # ============================================================================
# # ERROR HANDLERS - Custom error responses
# # ============================================================================

# @app.errorhandler(404)
# def not_found(error):
#     """Handle 404 errors (page not found)"""
#     return jsonify({'error': 'Endpoint not found'}), 404


# @app.errorhandler(500)
# def internal_error(error):
#     """Handle 500 errors (server errors)"""
#     return jsonify({'error': 'Internal server error'}), 500


# # ============================================================================
# # DATABASE INITIALIZATION
# # ============================================================================

# def init_db():
#     """
#     Create all database tables
#     Call this once when starting the project for the first time
#     """
#     with app.app_context():
#         db.create_all()
#         print("✅ Database tables created successfully!")


# # ============================================================================
# # RUN THE APP
# # ============================================================================

# if __name__ == '__main__':
#     # Create tables if they don't exist
#     init_db()
    
#     # Start the Flask development server
#     # debug=True enables auto-reload when code changes
#     # port=5000 means server runs at http://localhost:5000
#     app.run(debug=True, port=5000)


# backend/app.py
from flask import Flask, jsonify
from .config import Config
from .extensions import db
from .auth import bp as auth_bp
from .vendors import bp as vendors_bp
import os

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    db.init_app(app)

    # register blueprint(s)
    app.register_blueprint(auth_bp)
    app.register_blueprint(vendors_bp)


    @app.route("/")
    def home():
       return jsonify({
            "message": "FEMS Backend API is running!",
            "version": "1.0",
            "status": "active",
            "endpoints": {
                "register": "/api/register",
                "verify_email": "/api/verify-email",
                "complete_profile": "/api/complete-profile",
                "login": "/api/login",
                "profile": "/api/profile",
                "create_menu": "/api/vendors/<vendor_id>/menu",
                "add_items": "/api/vendors/<vendor_id>/menu/<menu_id>/items",
                "update_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
                "delete_item": "/api/vendors/<vendor_id>/menu/<menu_id>/items/<item_id>",
                "get_vendor": "/api/vendors/<vendor_id>"
            }
        })
    return app

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()  # creates tables according to models.py (including FK ondelete)
        print("✅ Database tables created successfully!")
    
    
    

    app.run(debug=True, port=5000)
