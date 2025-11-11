from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from dotenv import load_dotenv
from flask_wtf import wtfforms
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Read connection string and secret key from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SUPABASE_KEY')

# Create database instance (connection obj b/w flask and supabaseS)
db = SQLAlchemy(app)

# Define a User model (represents the email_verifications table in Supabase)
class User(db.Model, UserMixin):
    __tablename__ = 'email_verifications'  # must match your Supabase table name

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime, nullable=True)

# class RegisterForm(FlastForm):
#     username=StringFiled(validaors=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"username"})
#     password=StringFiled(validaors=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder":"username"})

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
