# backend/config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRES_DAYS = int(os.getenv("JWT_EXPIRES_DAYS", 7))
