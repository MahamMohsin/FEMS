# backend/customer_routes.py
"""
Customer Routes for FEMS
Features:
1. Browse all vendors
2. View vendor menu & items
3. Place order with cart items and pickup time
4. View order summary & status
5. View order history
"""

#blueprint for creating group of related routes
#request used to access incoming http requests
#jsonify converts python objects to json format
from flask import Blueprint, request, jsonify 
from .extensions import db
from .models import Vendor, Menu, MenuItem, Order, OrderItem, User
#token_required decorator to check if user is authenticated
from .auth import token_required
from datetime import datetime

#blueprint for customer routes which will be used to get all customer related routes
bp = Blueprint("customer", __name__, url_prefix="/api/customer")


