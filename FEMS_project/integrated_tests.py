"""
FEMS Complete System Integration Test
Tests both VENDOR and CUSTOMER flows in a single script
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


def print_section(title, color=BLUE):
    print(f"\n{color}{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}{RESET}\n")


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{CYAN}➤ {msg}{RESET}")


# ============================================================================
# VENDOR FLOW
# ============================================================================

def create_vendor():
    """Create a vendor account and set up menu"""
    print_section("🏪 VENDOR SETUP", MAGENTA)
    
    # 1. Register
    print_info("Registering vendor...")
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "pizza_palace@example.com",
        "password": "pizza123"
    })
    data = response.json()
    if response.status_code != 201:
        print_error(f"Registration failed: {data}")
        return None
    print_success("Vendor registered")
    verification_code = data["verification_code"]
    
    # 2. Verify email
    print_info("Verifying email...")
    response = requests.post(f"{BASE_URL}/api/verify-email", json={
        "email": "pizza_palace@example.com",
        "code": verification_code
    })
    if response.status_code != 200:
        print_error("Email verification failed")
        return None
    print_success("Email verified")
    
    # 3. Login
    print_info("Logging in...")
    response = requests.post(f"{BASE_URL}/api/login", json={
        "email": "pizza_palace@example.com",
        "password": "pizza123"
    })
    data = response.json()
    if response.status_code != 200:
        print_error("Login failed")
        return None
    vendor_token = data["token"]
    print_success("Vendor logged in")
    
    # 4. Complete profile
    print_info("Completing vendor profile...")
    response = requests.post(f"{BASE_URL}/api/complete-profile", 
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={
            "full_name": "Pizza Palace Owner",
            "phone": "1234567890",
            "role": "vendor",
            "vendor_name": "Pizza Palace",
            "location": "Campus Main Street"
        }
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Profile completion failed")
        return None
    vendor_id = data["vendor"]["id"]
    print_success(f"Vendor profile created (ID: {vendor_id})")
    
    # 5. Create menu
    print_info("Creating menu...")
    response = requests.post(f"{BASE_URL}/api/vendors/{vendor_id}/menu",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"title": "Main Menu"}
    )
    data = response.json()
    if response.status_code != 201:
        print_error("Menu creation failed")
        return None
    menu_id = data["menu"]["id"]
    print_success(f"Menu created (ID: {menu_id})")
    
    # 6. Add menu items
    print_info("Adding menu items...")
    response = requests.post(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json=[
            {
                "name": "Margherita Pizza",
                "price": 12.99,
                "description": "Classic tomato and mozzarella",
                "available": True,
                "preparation_time_minutes": 20
            },
            {
                "name": "Pepperoni Pizza",
                "price": 14.99,
                "description": "Loaded with pepperoni",
                "available": True,
                "preparation_time_minutes": 20
            },
            {
                "name": "Coke",
                "price": 2.99,
                "description": "Refreshing soda",
                "available": True,
                "preparation_time_minutes": 2
            }
        ]
    )
    data = response.json()
    if response.status_code != 201:
        print_error("Adding items failed")
        return None
    print_success(f"Added {len(data['items'])} menu items")
    
    print_section("✅ VENDOR SETUP COMPLETE", GREEN)
    print(f"Vendor ID: {vendor_id}")
    print(f"Menu ID: {menu_id}")
    print(f"Items: {len(data['items'])}")
    
    return {
        "vendor_id": vendor_id,
        "menu_id": menu_id,
        "token": vendor_token,
        "items": data["items"]
    }


# ============================================================================
# CUSTOMER FLOW
# ============================================================================

def create_customer_and_order(vendor_info):
    """Create customer account and place an order"""
    print_section("👤 CUSTOMER FLOW", CYAN)
    
    # 1. Register
    print_info("Registering customer...")
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "student@example.com",
        "password": "student123"
    })
    data = response.json()
    if response.status_code != 201:
        print_error(f"Registration failed: {data}")
        return None
    print_success("Customer registered")
    verification_code = data["verification_code"]
    
    # 2. Verify email
    print_info("Verifying email...")
    response = requests.post(f"{BASE_URL}/api/verify-email", json={
        "email": "student@example.com",
        "code": verification_code
    })
    if response.status_code != 200:
        print_error("Email verification failed")
        return None
    print_success("Email verified")
    
    # 3. Login
    print_info("Logging in...")
    response = requests.post(f"{BASE_URL}/api/login", json={
        "email": "student@example.com",
        "password": "student123"
    })
    data = response.json()
    if response.status_code != 200:
        print_error("Login failed")
        return None
    customer_token = data["token"]
    customer_id = data["user"]["id"]
    print_success("Customer logged in")
    
    # 4. Complete profile
    print_info("Completing customer profile...")
    response = requests.post(f"{BASE_URL}/api/complete-profile",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "full_name": "John Student",
            "phone": "9876543210",
            "role": "customer"
        }
    )
    if response.status_code != 200:
        print_error("Profile completion failed")
        return None
    print_success("Customer profile completed")
    
    # 5. Browse vendors
    print_info("Browsing available vendors...")
    response = requests.get(f"{BASE_URL}/api/customer/vendors",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Failed to browse vendors")
        return None
    print_success(f"Found {data['total']} vendor(s)")
    for vendor in data["vendors"]:
        print(f"  • {vendor['vendor_name']} - {vendor['location']}")
    
    # 6. View vendor menu
    print_info(f"Viewing menu for vendor {vendor_info['vendor_id']}...")
    response = requests.get(
        f"{BASE_URL}/api/customer/vendors/{vendor_info['vendor_id']}/menu",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Failed to view menu")
        return None
    menu = data["menu"]
    print_success(f"Menu loaded: {menu['title']}")
    print(f"  Items available: {len(menu['items'])}")
    for item in menu["items"]:
        print(f"    • {item['name']} - ${item['price']}")
    
    # 7. Place order
    print_info("Placing order...")
    pickup_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    
    # Select items from vendor's menu
    item_ids = [item["id"] for item in vendor_info["items"][:2]]  # First 2 items
    
    response = requests.post(f"{BASE_URL}/api/customer/orders",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "vendor_id": vendor_info["vendor_id"],
            "pickup_time": pickup_time,
            "pickup_or_delivery": "pickup",
            "order_notes": "Extra napkins please",
            "items": [
                {"menu_item_id": item_ids[0], "quantity": 2},
                {"menu_item_id": item_ids[1], "quantity": 1}
            ]
        }
    )
    data = response.json()
    if response.status_code != 201:
        print_error(f"Order placement failed: {data}")
        return None
    
    order_id = data["order"]["order_id"]
    total = data["order"]["total_amount"]
    print_success(f"Order placed successfully!")
    print(f"  Order ID: {order_id}")
    print(f"  Total: ${total}")
    print(f"  Status: {data['order']['status']}")
    
    # 8. View order details
    print_info(f"Fetching order details...")
    response = requests.get(f"{BASE_URL}/api/customer/orders/{order_id}",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Failed to fetch order details")
        return None
    print_success("Order details retrieved")
    print(f"  Vendor: {data['order']['vendor_name']}")
    print(f"  Items: {data['order']['items_count']}")
    print(f"  Total Quantity: {data['order']['total_quantity']}")
    
    # 9. View order history
    print_info("Viewing order history...")
    response = requests.get(f"{BASE_URL}/api/customer/orders",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Failed to fetch order history")
        return None
    print_success(f"Order history retrieved: {data['total']} order(s)")
    
    # 10. Get customer stats
    print_info("Fetching customer statistics...")
    response = requests.get(f"{BASE_URL}/api/customer/stats",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    data = response.json()
    if response.status_code != 200:
        print_error("Failed to fetch stats")
        return None
    stats = data["stats"]
    print_success("Statistics retrieved")
    print(f"  Total Orders: {stats['total_orders']}")
    print(f"  Total Spent: ${stats['total_spent']}")
    
    print_section("✅ CUSTOMER FLOW COMPLETE", GREEN)
    
    return {
        "customer_id": customer_id,
        "token": customer_token,
        "order_id": order_id
    }


# ============================================================================
# MAIN TEST
# ============================================================================

def main():
    print_section("🚀 FEMS COMPLETE SYSTEM INTEGRATION TEST", BLUE)
    print("This test demonstrates the complete flow:")
    print("1. Vendor creates account and sets up menu")
    print("2. Customer creates account")
    print("3. Customer browses vendors and places order")
    print()
    
    try:
        # Test server connection
        print_info("Checking server connection...")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print_error("Server health check failed")
            return
        print_success("Server is healthy")
        
        # Run vendor flow
        vendor_info = create_vendor()
        if not vendor_info:
            print_error("Vendor setup failed. Stopping test.")
            return
        
        # Run customer flow
        customer_info = create_customer_and_order(vendor_info)
        if not customer_info:
            print_error("Customer flow failed. Stopping test.")
            return
        
        # Final summary
        print_section("📊 TEST SUMMARY", GREEN)
        print(f"{GREEN}✅ All tests passed successfully!{RESET}")
        print()
        print("System Components Tested:")
        print(f"  ✓ Vendor Registration & Authentication")
        print(f"  ✓ Vendor Menu Management")
        print(f"  ✓ Customer Registration & Authentication")
        print(f"  ✓ Customer Vendor Browsing")
        print(f"  ✓ Customer Order Placement")
        print(f"  ✓ Order Tracking & History")
        print()
        print("Test Data:")
        print(f"  • Vendor ID: {vendor_info['vendor_id']}")
        print(f"  • Customer ID: {customer_info['customer_id']}")
        print(f"  • Order ID: {customer_info['order_id']}")
        print()
        print(f"{CYAN}{'='*80}{RESET}")
        print(f"{GREEN}🎉 FEMS System is fully operational!{RESET}")
        print(f"{CYAN}{'='*80}{RESET}\n")
        
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}❌ Cannot connect to server at {BASE_URL}{RESET}")
        print(f"Please ensure Flask server is running: python -m backend.app")
    except Exception as e:
        print(f"\n{RED}❌ Unexpected error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
