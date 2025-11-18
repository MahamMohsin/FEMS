

# import requests

# BASE_URL = "http://127.0.0.1:5000"

# # -------------------------------
# # 1️⃣ REGISTER
# # -------------------------------
# def test_register():
#     url = f"{BASE_URL}/api/register"
#     payload = {
#         "email": "test10@example.com",
#         "password": "password789"
#     }
#     response = requests.post(url, json=payload)
#     data = response.json()
#     print("=== REGISTER ===")
#     print("Status:", response.status_code)
#     print("Response:", data)
#     return data.get("verification_code")  # return verification code

# # -------------------------------
# # 2️⃣ VERIFY EMAIL
# # -------------------------------
# def test_verify_email(verification_code):
#     url = f"{BASE_URL}/api/verify-email"
#     payload = {
#         "email": "test10@example.com",
#         "code": verification_code
#     }
#     response = requests.post(url, json=payload)
#     print("=== VERIFY EMAIL ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # -------------------------------
# # 3️⃣ LOGIN
# # -------------------------------
# def test_login():
#     url = f"{BASE_URL}/api/login"
#     payload = {
#         "email": "test10@example.com",
#         "password": "password789"
#     }
#     response = requests.post(url, json=payload)
#     data = response.json()
#     print("=== LOGIN ===")
#     print("Status:", response.status_code)
#     print("Response:", data)
#     if response.status_code == 200:
#         return data["token"]  # return JWT token
#     return None

# # -------------------------------
# # 4️⃣ COMPLETE PROFILE (vendor)
# # -------------------------------
# def test_complete_profile(token):
#     url = f"{BASE_URL}/api/complete-profile"
#     payload = {
#         "full_name": "george Vendor",
#         "phone": "1234567890",
#         "role": "vendor",
#         "vendor_name": "george Cafe",
#         "location": "New York"
#     }
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()
#     print("=== COMPLETE PROFILE ===")
#     print("Status:", response.status_code)
#     print("Response:", data)
#     vendor_id = data.get("vendor", {}).get("id")
#     return vendor_id  # return vendor id for menu creation

# # -------------------------------
# # 5️⃣ CREATE MENU
# # -------------------------------
# def test_create_menu(token, vendor_id):
#     url = f"{BASE_URL}/api/vendors/{vendor_id}/menu"
#     payload = {"title": "Breakfast Menu"}
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(url, json=payload, headers=headers)
#     data = response.json()
#     print("=== CREATE MENU ===")
#     print("Status:", response.status_code)
#     print("Response:", data)
#     menu_id = data.get("menu", {}).get("id")
#     return menu_id

# # -------------------------------
# # 6️⃣ ADD MENU ITEMS
# # -------------------------------
# def test_add_menu_items(token, vendor_id, menu_id):
#     url = f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items"
#     payload = [
#         {
#             "name": "Pancakes",
#             "price": 5.99,
#             "description": "Fluffy pancakes",
#             "available": True,
#             "preparation_time_minutes": 15
#         },
#         {
#             "name": "Coffee",
#             "price": 2.99,
#             "description": "Hot black coffee",
#             "available": True,
#             "preparation_time_minutes": 5
#         }
#     ]
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(url, json=payload, headers=headers)
#     print("=== ADD MENU ITEMS ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # -------------------------------
# # 7️⃣ GET VENDOR INFO
# # -------------------------------
# def test_get_vendor(vendor_id):
#     url = f"{BASE_URL}/api/vendors/{vendor_id}"
#     response = requests.get(url)
#     print("=== GET VENDOR INFO ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # -------------------------------
# # RUN FULL FLOW
# # -------------------------------
# if __name__ == "__main__":
#     verification_code = test_register()
#     if verification_code:
#         test_verify_email(verification_code)
#         token = test_login()
#         if token:
#             vendor_id = test_complete_profile(token)
#             if vendor_id:
#                 menu_id = test_create_menu(token, vendor_id)
#                 if menu_id:
#                     test_add_menu_items(token, vendor_id, menu_id)
#                     test_get_vendor(vendor_id)

# test_auth_endpoints.py
"""
FEMS Backend API Testing Suite - Enhanced Version
===================================================
This file supports TWO testing modes:

MODE 1: FULL REGISTRATION FLOW
- Register new user
- Verify email
- Login
- Complete profile
- Create menu & items
- Update/Delete items

MODE 2: LOGIN-ONLY FLOW (Existing User)
- Login with existing credentials
- Access existing menu
- Add new items
- Update existing items
- Delete items

Usage:
------
# Test new user registration:
python test_auth_endpoints.py --mode register

# Test existing user login (vendor ID 4):
python test_auth_endpoints.py --mode login

# Run both tests:
python test_auth_endpoints.py --mode both

# Test specific vendor:
python test_auth_endpoints.py --mode login --vendor-id 4
"""

import requests
import json
import sys
import argparse

# Base URL for API
BASE_URL = "http://127.0.0.1:5000"

# ANSI color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


# ============================================================================
# TEST DATA CONFIGURATIONS
# ============================================================================

# Configuration for NEW USER (Registration Flow) - UNCHANGED
NEW_USER_CONFIG = {
    "email": "test10@example.com",
    "password": "password789",
    "full_name": "george Vendor",
    "phone": "1234567890",
    "role": "vendor",
    "vendor_name": "george Cafe",
    "location": "New York",
    "menu_title": "Breakfast Menu",
    "items_to_add": [
        {
            "name": "Pancakes",
            "price": 5.99,
            "description": "Fluffy pancakes",
            "available": True,
            "preparation_time_minutes": 15
        },
        {
            "name": "Coffee",
            "price": 2.99,
            "description": "Hot black coffee",
            "available": True,
            "preparation_time_minutes": 5
        }
    ],
    "update_item_data": {
        "name": "Premium Pancakes",
        "price": 6.99,
        "description": "Extra fluffy pancakes with toppings",
        "available": True,
        "preparation_time_minutes": 20
    }
}

# Configuration for EXISTING USER (Login-Only Flow) - CHANGED TO YOUR VENDOR
EXISTING_USER_CONFIG = {
    "email": "newvendor@example.com",    # YOUR EXISTING USER
    "password": "newpass123",            # YOUR EXISTING PASSWORD
    "vendor_id": 4,                      # YOUR VENDOR ID
    "items_to_add": [
        {
            "name": "Avocado Toast",
            "price": 9.99,
            "description": "Sourdough toast with smashed avocado, cherry tomatoes, and poached egg",
            "available": True,
            "preparation_time_minutes": 12,
            "image_url": "https://example.com/avocado-toast.jpg"
        }
    ],
    "update_item_data": {
        "name": "Premium Pancakes Deluxe",
        "price": 7.99,
        "description": "Extra fluffy pancakes with whipped cream, berries, and maple syrup",
        "available": True,
        "preparation_time_minutes": 25
    }
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_section(title, color=BLUE):
    """Print formatted section header"""
    print(f"\n{color}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{RESET}\n")


def print_response(status_code, data):
    """Print formatted response"""
    color = GREEN if 200 <= status_code < 300 else RED
    print(f"{color}Status: {status_code}{RESET}")
    print(f"Response: {json.dumps(data, indent=2)}\n")


def print_success(message):
    """Print success message"""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message"""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}{message}{RESET}")


def print_highlight(message):
    """Print highlighted message"""
    print(f"{CYAN}➤ {message}{RESET}")


# ============================================================================
# REGISTRATION FLOW TESTS
# ============================================================================

def test_register(config):
    """Test user registration"""
    print_section("1️⃣  REGISTER NEW USER", CYAN)
    
    url = f"{BASE_URL}/api/register"
    payload = {
        "email": config["email"],
        "password": config["password"]
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    print_response(response.status_code, data)
    
    verification_code = data.get("verification_code")
    
    if response.status_code == 201:
        print_success("User registered successfully")
        print_info(f"Verification Code: {verification_code}")
        return verification_code
    elif response.status_code == 409:
        print_error("Email already registered - use login mode instead")
        return None
    else:
        print_error("Registration failed")
        return None


def test_verify_email(email, verification_code):
    """Test email verification"""
    print_section("2️⃣  VERIFY EMAIL", CYAN)
    
    url = f"{BASE_URL}/api/verify-email"
    payload = {
        "email": email,
        "code": verification_code
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        print_success("Email verified successfully")
        return True
    else:
        print_error("Email verification failed")
        return False


def test_complete_profile(token, config):
    """Test profile completion"""
    print_section("4️⃣  COMPLETE PROFILE (VENDOR)", CYAN)
    
    url = f"{BASE_URL}/api/complete-profile"
    payload = {
        "full_name": config["full_name"],
        "phone": config["phone"],
        "role": config["role"],
        "vendor_name": config["vendor_name"],
        "location": config["location"]
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        vendor_id = data.get("vendor", {}).get("id")
        print_success("Profile completed successfully")
        print_info(f"Vendor ID: {vendor_id}")
        return vendor_id
    else:
        print_error("Profile completion failed")
        return None


# ============================================================================
# COMMON TESTS (Used by both flows)
# ============================================================================

def test_login(config):
    """Test user login"""
    print_section("3️⃣  LOGIN USER", MAGENTA)
    
    url = f"{BASE_URL}/api/login"
    payload = {
        "email": config["email"],
        "password": config["password"]
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        token = data.get("token")
        user = data.get("user", {})
        print_success("Login successful")
        print_info(f"User ID: {user.get('id')}")
        print_info(f"Email: {user.get('email')}")
        print_info(f"Name: {user.get('full_name')}")
        print_info(f"Role: {user.get('role')}")
        print_info(f"Email Verified: {user.get('is_email_verified')}")
        print_info(f"JWT Token: {token[:50]}...")
        return token, user
    else:
        print_error("Login failed")
        return None, None


def get_existing_vendor_info(vendor_id):
    """Get existing vendor's complete information"""
    print_section("📋  FETCHING EXISTING VENDOR DATA", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print_error(f"Failed to fetch vendor {vendor_id}")
        return None, None, []
    
    data = response.json()
    vendor = data.get("vendor", {})
    menu = vendor.get("menu")
    items = menu.get("items", []) if menu else []
    
    print_success("Vendor data retrieved successfully")
    print_info(f"Vendor Name: {vendor.get('vendor_name')}")
    print_info(f"Location: {vendor.get('location')}")
    print_info(f"Pickup Available: {vendor.get('pickup_available')}")
    print_info(f"Delivery Available: {vendor.get('delivery_available')}")
    
    if menu:
        menu_id = menu.get("id")
        print_info(f"Menu ID: {menu_id}")
        print_info(f"Menu Title: {menu.get('title')}")
        print_info(f"Menu Active: {menu.get('is_active')}")
        print_info(f"Total Items: {len(items)}")
        
        if items:
            print(f"\n{CYAN}Existing Menu Items:{RESET}")
            for item in items:
                status = "✓ Available" if item['available'] else "✗ Unavailable"
                print(f"  • ID {item['id']}: {item['name']} - ${item['price']} ({status})")
                print(f"    Description: {item['description']}")
                print(f"    Prep Time: {item['preparation_time_minutes']} min")
    else:
        print_info("No menu found for this vendor")
        menu_id = None
    
    return vendor, menu_id, items


def test_create_menu(token, vendor_id, config):
    """Test menu creation"""
    print_section("5️⃣  CREATE/GET MENU", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu"
    payload = {"title": config.get("menu_title", "Main Menu")}
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 201:
        menu_id = data.get("menu", {}).get("id")
        print_success("Menu created successfully")
        print_info(f"Menu ID: {menu_id}")
        return menu_id
    elif response.status_code == 409:
        print_info("Menu already exists - fetching existing menu")
        return get_existing_menu_id(vendor_id)
    else:
        print_error("Menu creation failed")
        return None


def get_existing_menu_id(vendor_id):
    """Get existing menu ID for a vendor"""
    url = f"{BASE_URL}/api/vendors/{vendor_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        vendor_data = response.json().get("vendor", {})
        menu = vendor_data.get("menu")
        if menu:
            menu_id = menu.get("id")
            print_success(f"Found existing menu: {menu.get('title')} (ID: {menu_id})")
            return menu_id
    
    return None


def test_add_menu_items(token, vendor_id, menu_id, config):
    """Test adding menu items"""
    print_section("6️⃣  ADD NEW MENU ITEMS", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items"
    payload = config["items_to_add"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print_highlight(f"Adding {len(payload)} new item(s):")
    for item in payload:
        print(f"  • {item['name']} - ${item['price']}")
    
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 201:
        items = data.get("items", [])
        print_success(f"{len(items)} item(s) added successfully")
        
        # Display added items
        print(f"\n{CYAN}Newly Added Items:{RESET}")
        for item in items:
            print(f"  • ID {item['id']}: {item['name']} - ${item['price']}")
        
        item_ids = [item["id"] for item in items]
        return item_ids
    else:
        print_error("Adding items failed")
        return []


def test_update_menu_item(token, vendor_id, menu_id, item_id, config, item_name=""):
    """Test updating a menu item"""
    print_section("7️⃣  UPDATE MENU ITEM", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_id}"
    payload = config["update_item_data"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print_highlight(f"Updating Item ID: {item_id} {f'({item_name})' if item_name else ''}")
    print_info("New data:")
    for key, value in payload.items():
        print(f"  • {key}: {value}")
    
    response = requests.put(url, json=payload, headers=headers)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        updated_item = data.get("item", {})
        print_success("Menu item updated successfully")
        print(f"\n{CYAN}Updated Item Details:{RESET}")
        print(f"  • ID: {updated_item.get('id')}")
        print(f"  • Name: {updated_item.get('name')}")
        print(f"  • Price: ${updated_item.get('price')}")
        print(f"  • Description: {updated_item.get('description')}")
        print(f"  • Available: {updated_item.get('available')}")
        print(f"  • Prep Time: {updated_item.get('preparation_time_minutes')} min")
        return True
    else:
        print_error("Update failed")
        return False


def test_delete_menu_item(token, vendor_id, menu_id, item_id, item_name=""):
    """Test deleting a menu item"""
    print_section("8️⃣  DELETE MENU ITEM", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    print_highlight(f"Deleting Item ID: {item_id} {f'({item_name})' if item_name else ''}")
    
    response = requests.delete(url, headers=headers)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        deleted_item = data.get("deleted_item", {})
        print_success("Menu item deleted successfully")
        print(f"\n{CYAN}Deleted Item:{RESET}")
        print(f"  • ID: {deleted_item.get('id')}")
        print(f"  • Name: {deleted_item.get('name')}")
        print(f"  • Price: ${deleted_item.get('price')}")
        return True
    else:
        print_error("Deletion failed")
        return False


def test_get_vendor(vendor_id):
    """Test getting vendor information"""
    print_section("9️⃣  FINAL VENDOR STATE (VERIFY ALL CHANGES)", MAGENTA)
    
    url = f"{BASE_URL}/api/vendors/{vendor_id}"
    response = requests.get(url)
    data = response.json()
    print_response(response.status_code, data)
    
    if response.status_code == 200:
        vendor = data.get("vendor", {})
        menu = vendor.get("menu", {})
        items = menu.get("items", [])
        
        print_success("Vendor info retrieved successfully")
        
        print(f"\n{CYAN}{'='*70}{RESET}")
        print(f"{CYAN}VENDOR SUMMARY{RESET}")
        print(f"{CYAN}{'='*70}{RESET}")
        print(f"Vendor ID: {vendor.get('id')}")
        print(f"Name: {vendor.get('vendor_name')}")
        print(f"Location: {vendor.get('location')}")
        print(f"Pickup: {vendor.get('pickup_available')}")
        print(f"Delivery: {vendor.get('delivery_available')}")
        
        print(f"\n{CYAN}MENU SUMMARY{RESET}")
        print(f"Menu ID: {menu.get('id')}")
        print(f"Title: {menu.get('title')}")
        print(f"Active: {menu.get('is_active')}")
        print(f"Total Items: {len(items)}")
        
        if items:
            print(f"\n{CYAN}ALL MENU ITEMS:{RESET}")
            for idx, item in enumerate(items, 1):
                status = f"{GREEN}✓ Available{RESET}" if item['available'] else f"{RED}✗ Unavailable{RESET}"
                print(f"\n{idx}. {item['name']} (ID: {item['id']})")
                print(f"   Price: ${item['price']}")
                print(f"   Status: {status}")
                print(f"   Description: {item['description']}")
                print(f"   Prep Time: {item['preparation_time_minutes']} minutes")
                if item.get('image_url'):
                    print(f"   Image: {item['image_url']}")
        else:
            print(f"\n{YELLOW}No items in menu{RESET}")
            
        return items
    else:
        print_error("Failed to get vendor info")
        return []


# ============================================================================
# MAIN TEST FLOWS
# ============================================================================

def run_registration_flow():
    """
    Complete registration flow for NEW users
    Tests: Register → Verify → Login → Profile → Menu → Items → Update → Delete
    """
    print(f"\n{CYAN}{'='*70}")
    print(f"  🆕 TESTING: NEW USER REGISTRATION FLOW")
    print(f"{'='*70}{RESET}\n")
    
    config = NEW_USER_CONFIG
    
    # Step 1: Register
    verification_code = test_register(config)
    if not verification_code:
        print_error("\n❌ Test suite stopped: Registration failed")
        return
    
    # Step 2: Verify Email
    if not test_verify_email(config["email"], verification_code):
        print_error("\n❌ Test suite stopped: Email verification failed")
        return
    
    # Step 3: Login
    token, user = test_login(config)
    if not token:
        print_error("\n❌ Test suite stopped: Login failed")
        return
    
    # Step 4: Complete Profile
    vendor_id = test_complete_profile(token, config)
    if not vendor_id:
        print_error("\n❌ Test suite stopped: Profile completion failed")
        return
    
    # Step 5: Create Menu
    menu_id = test_create_menu(token, vendor_id, config)
    if not menu_id:
        print_error("\n❌ Test suite stopped: Menu creation failed")
        return
    
    # Step 6: Add Items
    item_ids = test_add_menu_items(token, vendor_id, menu_id, config)
    if not item_ids:
        print_error("\n❌ Test suite stopped: Adding items failed")
        return
    
    # Step 7: Update First Item
    if len(item_ids) > 0:
        test_update_menu_item(token, vendor_id, menu_id, item_ids[0], config, "Pancakes")
    
    # Step 8: Delete Second Item
    if len(item_ids) > 1:
        test_delete_menu_item(token, vendor_id, menu_id, item_ids[1], "Coffee")
    
    # Step 9: Verify Changes
    test_get_vendor(vendor_id)
    
    print(f"\n{GREEN}{'='*70}")
    print(f"  ✅ REGISTRATION FLOW COMPLETED!")
    print(f"{'='*70}{RESET}\n")


def run_login_flow(vendor_id_override=None):
    """
    Login-only flow for EXISTING users
    Tests: Login → Get Vendor → Add Item → Update Item → Delete Item
    
    This is designed for vendor ID 4 (newvendor@example.com)
    """
    print(f"\n{MAGENTA}{'='*70}")
    print(f"  🔑 TESTING: EXISTING USER LOGIN FLOW")
    print(f"  Vendor: newvendor@example.com (ID: 4)")
    print(f"{'='*70}{RESET}\n")
    
    config = EXISTING_USER_CONFIG
    
    # Use override vendor_id if provided
    vendor_id = vendor_id_override or config["vendor_id"]
    
    # Step 1: Login
    print_info("Logging in to existing vendor account...")
    print_info(f"Email: {config['email']}")
    print_info(f"Vendor ID: {vendor_id}\n")
    
    token, user = test_login(config)
    if not token:
        print_error("\n❌ Test suite stopped: Login failed")
        print_info("💡 Make sure the user exists and credentials are correct")
        return
    
    # Step 2: Get existing vendor data
    vendor, menu_id, existing_items = get_existing_vendor_info(vendor_id)
    
    if not vendor:
        print_error(f"\n❌ Test suite stopped: Vendor {vendor_id} not found")
        return
    
    if not menu_id:
        print_info("\n📝 No menu found. Creating one...")
        menu_id = test_create_menu(token, vendor_id, config)
        if not menu_id:
            print_error("\n❌ Test suite stopped: Menu creation failed")
            return
        existing_items = []
    
    # Step 3: Add NEW item (Avocado Toast)
    print_highlight("\n📌 OPERATION 1: Adding new menu item")
    new_item_ids = test_add_menu_items(token, vendor_id, menu_id, config)
    
    # Step 4: Update EXISTING item (first item from existing menu)
    if existing_items and len(existing_items) > 0:
        print_highlight("\n📌 OPERATION 2: Updating existing menu item")
        item_to_update = existing_items[0]
        test_update_menu_item(
            token, vendor_id, menu_id, 
            item_to_update['id'], 
            config, 
            item_to_update['name']
        )
    else:
        print_info("\n⚠️  No existing items to update. Skipping update operation.")
    
    # Step 5: Delete EXISTING item (second item from existing menu)
    if existing_items and len(existing_items) > 1:
        print_highlight("\n📌 OPERATION 3: Deleting existing menu item")
        item_to_delete = existing_items[1]
        test_delete_menu_item(
            token, vendor_id, menu_id, 
            item_to_delete['id'], 
            item_to_delete['name']
        )
    else:
        print_info("\n⚠️  Not enough existing items to delete. Skipping delete operation.")
    
    # Step 6: Verify all changes
    print_highlight("\n📌 FINAL VERIFICATION")
    final_items = test_get_vendor(vendor_id)
    
    # Summary
    print(f"\n{GREEN}{'='*70}")
    print(f"  ✅ LOGIN FLOW COMPLETED!")
    print(f"{'='*70}{RESET}")
    print(f"\n{CYAN}OPERATIONS SUMMARY:{RESET}")
    print(f"  • Logged in as: {config['email']}")
    print(f"  • Vendor ID: {vendor_id}")
    print(f"  • Items at start: {len(existing_items)}")
    print(f"  • Items added: {len(new_item_ids) if new_item_ids else 0}")
    print(f"  • Items updated: {1 if existing_items and len(existing_items) > 0 else 0}")
    print(f"  • Items deleted: {1 if existing_items and len(existing_items) > 1 else 0}")
    print(f"  • Items at end: {len(final_items)}")
    print(f"{GREEN}{'='*70}{RESET}\n")


def run_both_flows():
    """Run both registration and login flows"""
    print(f"\n{BLUE}{'='*70}")
    print(f"  🚀 RUNNING COMPLETE TEST SUITE")
    print(f"  Testing both NEW and EXISTING user flows")
    print(f"{'='*70}{RESET}\n")
    
    # First run registration flow
    run_registration_flow()
    
    # Pause between tests
    print(f"\n{YELLOW}{'='*70}")
    print(f"  ⏸️  Pausing before next test...")
    print(f"{'='*70}{RESET}\n")
    input(f"{YELLOW}Press Enter to continue with Login Flow test...{RESET}")
    
    # Then run login flow
    run_login_flow()
    
    print(f"\n{GREEN}{'='*70}")
    print(f"  ✅ ALL TESTS COMPLETED!")
    print(f"{'='*70}{RESET}\n")


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='FEMS Backend API Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test new user registration flow:
  python test_auth_endpoints.py --mode register

  # Test existing user (vendor ID 4 - newvendor@example.com):
  python test_auth_endpoints.py --mode login

  # Test specific vendor:
  python test_auth_endpoints.py --mode login --vendor-id 5

  # Run both flows:
  python test_auth_endpoints.py --mode both
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['register', 'login', 'both'],
        default='register',
        help='Test mode: register (new user), login (existing user), or both'
    )
    
    parser.add_argument(
        '--vendor-id',
        type=int,
        default=None,
        help='Specify vendor ID for login mode (default: 4 for newvendor@example.com)'
    )
    
    args = parser.parse_args()
    
    # Display test configuration
    print(f"\n{BLUE}{'='*70}")
    print(f"  FEMS BACKEND API - TEST CONFIGURATION")
    print(f"{'='*70}{RESET}")
    print(f"Mode: {args.mode}")
    print(f"Base URL: {BASE_URL}")
    if args.mode == 'login':
        vendor_id = args.vendor_id or EXISTING_USER_CONFIG['vendor_id']
        print(f"Target Vendor ID: {vendor_id}")
        print(f"Login Email: {EXISTING_USER_CONFIG['email']}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        if args.mode == 'register':
            run_registration_flow()
        elif args.mode == 'login':
            run_login_flow(args.vendor_id)
        elif args.mode == 'both':
            run_both_flows()
            
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}{'='*70}")
        print(f"  ❌ ERROR: Cannot connect to Flask server")
        print(f"  Please ensure the server is running on {BASE_URL}")
        print(f"  Start server with: python -m backend.app")
        print(f"{'='*70}{RESET}\n")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}{'='*70}")
        print(f"  ⚠️  Tests interrupted by user")
        print(f"{'='*70}{RESET}\n")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n{RED}{'='*70}")
        print(f"  ❌ UNEXPECTED ERROR: {str(e)}")
        print(f"{'='*70}{RESET}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()