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

# Update menu items
@bp.route("/<int:vendor_id>/menu/<int:menu_id>/items/<int:item_id>", methods=["PUT"])
@token_required
def update_menu_item(current_user, vendor_id, menu_id, item_id):
    """
    Update an existing menu item
    
    Flow:
    1. Verify vendor ownership
    2. Verify menu belongs to vendor
    3. Find the specific menu item
    4. Update only provided fields (partial update supported)
    5. Save changes
    
    Updatable Fields:
    - name: Item name
    - description: Item description
    - price: Item price
    - available: Whether item is available
    - preparation_time_minutes: Time to prepare
    - image_url: Image URL
    
    Expected JSON (all fields optional):
    {
        "name": "Updated Pancakes",
        "price": 6.99,
        "description": "Extra fluffy pancakes",
        "available": false,
        "preparation_time_minutes": 20,
        "image_url": "https://example.com/new-pancake.jpg"
    }
    
    Returns:
    - 200: Item updated successfully
    - 403: User doesn't own vendor
    - 404: Vendor, menu, or item not found
    """
    # Verify vendor exists and user owns it
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.user_id != current_user.id:
        return jsonify({"error": "forbidden or vendor not found"}), 403

    # Verify menu exists and belongs to vendor
    menu = Menu.query.get(menu_id)
    if not menu or menu.vendor_id != vendor_id:
        return jsonify({"error": "menu not found"}), 404

    # Find the specific menu item
    # Check it belongs to this menu AND vendor (double security)
    menu_item = MenuItem.query.filter_by(
        id=item_id,
        menu_id=menu_id,
        vendor_id=vendor_id
    ).first()
    
    if not menu_item:
        return jsonify({"error": "menu item not found"}), 404

    # Get update data from request
    data = request.get_json() or {}

    # Update only fields that are provided
    # This allows partial updates (e.g., only updating price)
    
    if "name" in data:
        name = data["name"].strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        menu_item.name = name

    if "description" in data:
        menu_item.description = data["description"].strip()

    if "price" in data:
        price = data["price"]
        if price is None or price < 0:
            return jsonify({"error": "price must be a positive number"}), 400
        menu_item.price = price

    if "available" in data:
        # Convert to boolean
        menu_item.available = bool(data["available"])

    if "preparation_time_minutes" in data:
        prep_time = data["preparation_time_minutes"]
        if prep_time is None or prep_time < 0:
            return jsonify({"error": "preparation_time_minutes must be positive"}), 400
        menu_item.preparation_time_minutes = prep_time

    if "image_url" in data:
        menu_item.image_url = data["image_url"].strip()

    # Save changes to database
    try:
        db.session.commit()
        return jsonify({
            "message": "menu item updated successfully",
            "item": menu_item.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "db error", "details": str(e)}), 500

#delete menu items:
@bp.route("/<int:vendor_id>/menu/<int:menu_id>/items/<int:item_id>", methods=["DELETE"])
@token_required
def delete_menu_item(current_user, vendor_id, menu_id, item_id):
    """
    Delete a menu item
    
    Flow:
    1. Verify vendor ownership
    2. Verify menu belongs to vendor
    3. Find and verify menu item
    4. Delete from database
    
    IMPORTANT: This is a hard delete. The item will be permanently removed.
    Consider implementing soft delete (setting available=False) if you want
    to preserve order history.
    
    Returns:
    - 200: Item deleted successfully
    - 403: User doesn't own vendor
    - 404: Vendor, menu, or item not found
    """
    # Verify vendor exists and user owns it
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.user_id != current_user.id:
        return jsonify({"error": "forbidden or vendor not found"}), 403

    # Verify menu exists and belongs to vendor
    menu = Menu.query.get(menu_id)
    if not menu or menu.vendor_id != vendor_id:
        return jsonify({"error": "menu not found"}), 404

    # Find the specific menu item
    menu_item = MenuItem.query.filter_by(
        id=item_id,
        menu_id=menu_id,
        vendor_id=vendor_id
    ).first()
    
    if not menu_item:
        return jsonify({"error": "menu item not found"}), 404

    # Store item details for response before deletion
    item_data = menu_item.to_dict()

    # Delete from database
    try:
        db.session.delete(menu_item)
        db.session.commit()
        return jsonify({
            "message": "menu item deleted successfully",
            "deleted_item": item_data
        }), 200
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
