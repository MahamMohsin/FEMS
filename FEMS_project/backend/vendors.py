# backend/vendors.py
from flask import Blueprint, request, jsonify
from .extensions import db
from .models import Vendor, Menu, MenuItem
from .auth import token_required
from datetime import datetime

bp = Blueprint("vendors", __name__, url_prefix="/api/vendors")

# Create menu for a vendor (only owner)
@bp.route("/<int:vendor_id>/menu", methods=["POST"])
@token_required
def create_menu(current_user, vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "vendor not found"}), 404
    if vendor.user_id != current_user.id:
        return jsonify({"error": "forbidden"}), 403

    if vendor.menu:
        return jsonify({"error": "menu already exists"}), 409

    data = request.get_json() or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    menu = Menu(vendor_id=vendor_id, title=title)
    try:
        db.session.add(menu)
        db.session.commit()
        return jsonify({"message": "menu created", "menu": menu.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "db error", "details": str(e)}), 500

# Add menu items (single or list)
@bp.route("/<int:vendor_id>/menu/<int:menu_id>/items", methods=["POST"])
@token_required
def add_menu_items(current_user, vendor_id, menu_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.user_id != current_user.id:
        return jsonify({"error": "forbidden or vendor not found"}), 403

    menu = Menu.query.get(menu_id)
    if not menu or menu.vendor_id != vendor_id:
        return jsonify({"error": "menu not found"}), 404

    payload = request.get_json() or {}
    items = payload if isinstance(payload, list) else [payload]

    created = []
    try:
        for item in items:
            name = (item.get("name") or "").strip()
            price = item.get("price", None)
            if not name or price is None:
                return jsonify({"error": "each item requires name and price"}), 400

            mi = MenuItem(
                menu_id=menu_id,
                vendor_id=vendor_id,
                name=name,
                description=item.get("description", ""),
                price=item.get("price"),
                available=item.get("available", True),
                preparation_time_minutes=item.get("preparation_time_minutes", 15),
                image_url=item.get("image_url", "")
            )
            db.session.add(mi)
            db.session.flush()  # get id
            created.append(mi.to_dict())
        db.session.commit()
        return jsonify({"message": "items created", "items": created}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "db error", "details": str(e)}), 500

# Get vendor detail (menu + items)
@bp.route("/<int:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor:
        return jsonify({"error": "vendor not found"}), 404
    return jsonify({"vendor": vendor.to_dict()}), 200
