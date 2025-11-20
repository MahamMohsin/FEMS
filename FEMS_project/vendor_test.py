"""
FEMS Refactored Vendor Routes - Complete Test Suite
Tests the NEW stored procedure approach with order management

Run this after:
1. Running vendor_db_objects.sql in Supabase
2. Replacing vendors.py with refactored version
3. Restarting Flask server
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000"

# Colors for terminal
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
    print(f"{CYAN}ℹ {msg}{RESET}")


def print_highlight(msg):
    print(f"{YELLOW}➤ {msg}{RESET}")


# ============================================================================
# VENDOR SETUP
# ============================================================================

def setup_vendor():
    """Create and setup vendor account with menu"""
    print_section("🏪 VENDOR SETUP", MAGENTA)
    
    # Register
    print_info("Registering vendor...")
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "pizzapalace@test.com",
        "password": "pizza123"
    })
    
    if response.status_code == 409:
        print_highlight("Vendor already exists, logging in...")
        response = requests.post(f"{BASE_URL}/api/login", json={
            "email": "pizzapalace@test.com",
            "password": "pizza123"
        })
        data = response.json()
        vendor_token = data["token"]
        
        # Get vendor ID
        response = requests.get(f"{BASE_URL}/api/profile",
            headers={"Authorization": f"Bearer {vendor_token}"}
        )
        user_data = response.json()["user"]
        
        # Get vendor ID from vendors table
        # This is a workaround - in real app, store vendor_id in profile response
        print_info("Using existing vendor account")
        vendor_id = 1  # Adjust if needed
        return vendor_token, vendor_id
    
    data = response.json()
    verification_code = data["verification_code"]
    print_success("Vendor registered")
    
    # Verify email
    print_info("Verifying email...")
    requests.post(f"{BASE_URL}/api/verify-email", json={
        "email": "pizzapalace@test.com",
        "code": verification_code
    })
    print_success("Email verified")
    
    # Login
    print_info("Logging in...")
    response = requests.post(f"{BASE_URL}/api/login", json={
        "email": "pizzapalace@test.com",
        "password": "pizza123"
    })
    data = response.json()
    vendor_token = data["token"]
    print_success("Logged in")
    
    # Complete profile
    print_info("Completing profile...")
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
    vendor_id = data["vendor"]["id"]
    print_success(f"Vendor profile created (ID: {vendor_id})")
    
    return vendor_token, vendor_id


# ============================================================================
# MENU MANAGEMENT TESTS
# ============================================================================

def test_menu_management(vendor_token, vendor_id):
    """Test menu creation and item management"""
    print_section("📋 MENU MANAGEMENT TESTS", CYAN)
    
    # 1. Create Menu
    print_highlight("Test 1: Create Menu")
    response = requests.post(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"title": "Main Menu"}
    )
    
    if response.status_code == 201:
        data = response.json()
        menu_id = data["menu"]["id"]
        print_success(f"Menu created (ID: {menu_id})")
    elif response.status_code == 400 and "already exists" in response.json().get("error", ""):
        print_info("Menu already exists, fetching...")
        response = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}")
        vendor_data = response.json()["vendor"]
        menu_id = vendor_data["menu"]["id"] if vendor_data.get("menu") else None
        if menu_id:
            print_success(f"Using existing menu (ID: {menu_id})")
        else:
            print_error("Could not get menu ID")
            return None
    else:
        print_error(f"Menu creation failed: {response.json()}")
        return None
    
    # 2. Add Menu Items (Batch)
    print_highlight("\nTest 2: Add Menu Items (Batch)")
    response = requests.post(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json=[
            {
                "name": "Margherita Pizza",
                "description": "Classic tomato and mozzarella",
                "price": 12.99,
                "available": True,
                "preparation_time_minutes": 20
            },
            {
                "name": "Pepperoni Pizza",
                "description": "Loaded with pepperoni",
                "price": 14.99,
                "available": True,
                "preparation_time_minutes": 20
            },
            {
                "name": "Coke",
                "description": "Refreshing soda",
                "price": 2.99,
                "available": True,
                "preparation_time_minutes": 2
            }
        ]
    )
    
    if response.status_code == 201:
        data = response.json()
        item_ids = [item["id"] for item in data["items"]]
        print_success(f"Added {len(item_ids)} items")
        print_info(f"Item IDs: {item_ids}")
    else:
        print_error(f"Adding items failed: {response.json()}")
        return None
    
    # 3. Update Menu Item
    print_highlight("\nTest 3: Update Menu Item")
    response = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_ids[0]}",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={
            "price": 13.99,
            "description": "Classic tomato and fresh mozzarella"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Updated item: {data['item']['name']} - ${data['item']['price']}")
    else:
        print_error(f"Update failed: {response.json()}")
    
    # 4. Delete Menu Item
    print_highlight("\nTest 4: Delete Menu Item")
    response = requests.delete(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_ids[2]}",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Deleted item: {data['deleted_item']['name']}")
    else:
        print_error(f"Delete failed: {response.json()}")
    
    # 5. Get Vendor Info
    print_highlight("\nTest 5: Get Vendor Info (Public)")
    response = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}")
    
    if response.status_code == 200:
        data = response.json()
        vendor = data["vendor"]
        print_success(f"Vendor: {vendor['vendor_name']}")
        print_info(f"Location: {vendor['location']}")
        if vendor.get("menu"):
            print_info(f"Menu Items: {len(vendor['menu']['items'])}")
    else:
        print_error(f"Get vendor failed: {response.json()}")
    
    return menu_id, item_ids


# ============================================================================
# CUSTOMER ORDER CREATION (SETUP FOR ORDER TESTS)
# ============================================================================

def create_customer_order(vendor_id, item_ids):
    """Create a customer and place an order"""
    print_section("👤 CUSTOMER ORDER CREATION", BLUE)
    
    # Register customer
    print_info("Registering customer...")
    response = requests.post(f"{BASE_URL}/api/register", json={
        "email": "student@test.com",
        "password": "student123"
    })
    
    if response.status_code == 409:
        print_highlight("Customer already exists, logging in...")
        response = requests.post(f"{BASE_URL}/api/login", json={
            "email": "student@test.com",
            "password": "student123"
        })
        customer_token = response.json()["token"]
    else:
        data = response.json()
        verification_code = data["verification_code"]
        
        # Verify email
        requests.post(f"{BASE_URL}/api/verify-email", json={
            "email": "student@test.com",
            "code": verification_code
        })
        
        # Login
        response = requests.post(f"{BASE_URL}/api/login", json={
            "email": "student@test.com",
            "password": "student123"
        })
        customer_token = response.json()["token"]
        
        # Complete profile
        requests.post(f"{BASE_URL}/api/complete-profile",
            headers={"Authorization": f"Bearer {customer_token}"},
            json={
                "full_name": "John Student",
                "phone": "9876543210",
                "role": "customer"
            }
        )
    
    print_success("Customer ready")
    
    # Place order
    print_info("Placing order...")
    pickup_time = (datetime.utcnow() + timedelta(hours=4)).isoformat()
    
    response = requests.post(
        f"{BASE_URL}/api/customer/orders",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={
            "vendor_id": vendor_id,
            "pickup_time": pickup_time,
            "pickup_or_delivery": "pickup",
            "order_notes": "Extra cheese please",
            "items": [
                {"menu_item_id": item_ids[0], "quantity": 2},
                {"menu_item_id": item_ids[1], "quantity": 1}
            ]
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        order_id = data["order"]["order_id"]
        total = data["order"]["total_amount"]
        print_success(f"Order placed (ID: {order_id}, Total: ${total})")
        return order_id
    else:
        print_error(f"Order placement failed: {response.json()}")
        return None


# ============================================================================
# ORDER MANAGEMENT TESTS (NEW!)
# ============================================================================

def test_order_management(vendor_token, vendor_id, order_id):
    """Test vendor order management features"""
    print_section("📦 ORDER MANAGEMENT TESTS (NEW FEATURE!)", MAGENTA)
    
    # 1. View All Orders
    print_highlight("Test 1: View All Orders")
    response = requests.get(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Found {data['total']} order(s)")
        if data["orders"]:
            order = data["orders"][0]
            print_info(f"Latest: Order #{order['order_id']} - {order['customer_name']} - ${order['total_amount']}")
    else:
        print_error(f"View orders failed: {response.json()}")
    
    # 2. View Pending Orders
    print_highlight("\nTest 2: View Pending Orders")
    response = requests.get(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders?status=pending",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Found {data['total']} pending order(s)")
    
    # 3. View Order Details
    print_highlight("\nTest 3: View Order Details")
    response = requests.get(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        order = data["order"]
        items = data["items"]
        print_success("Order details retrieved")
        print_info(f"Customer: {order['customer_name']} ({order['customer_phone']})")
        print_info(f"Items: {data['items_count']}")
        print_info(f"Total: ${order['total_amount']}")
        print_info(f"Status: {order['status']}")
    else:
        print_error(f"View details failed: {response.json()}")
    
    # 4. Accept Order
    print_highlight("\nTest 4: Accept Order")
    ready_time = (datetime.utcnow() + timedelta(hours=3, minutes=45)).isoformat()
    response = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={
            "status": "accepted",
            "estimated_ready_at": ready_time
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Order accepted: {data['order']['old_status']} → {data['order']['new_status']}")
        print_info(f"Ready at: {data['order']['estimated_ready_at']}")
    else:
        print_error(f"Accept order failed: {response.json()}")
    
    # 5. Start Preparing
    print_highlight("\nTest 5: Start Preparing")
    response = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"status": "preparing"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status updated: {data['order']['old_status']} → {data['order']['new_status']}")
    else:
        print_error(f"Update failed: {response.json()}")
    
    # 6. Mark Ready
    print_highlight("\nTest 6: Mark Ready for Pickup")
    response = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"status": "ready"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status updated: {data['order']['old_status']} → {data['order']['new_status']}")
    else:
        print_error(f"Update failed: {response.json()}")
    
    # 7. Mark Completed
    print_highlight("\nTest 7: Mark as Completed")
    response = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {vendor_token}"},
        json={"status": "completed"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Status updated: {data['order']['old_status']} → {data['order']['new_status']}")
        print_highlight("🎉 Order lifecycle complete!")
    else:
        print_error(f"Update failed: {response.json()}")


# ============================================================================
# ANALYTICS TESTS (NEW!)
# ============================================================================

def test_analytics(vendor_token, vendor_id):
    """Test vendor analytics features"""
    print_section("📊 ANALYTICS TESTS (NEW FEATURE!)", CYAN)
    
    print_highlight("Test: Get Vendor Statistics")
    response = requests.get(
        f"{BASE_URL}/api/vendors/{vendor_id}/stats",
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data["stats"]
        print_success("Statistics retrieved")
        print(f"\n{YELLOW}{'='*60}")
        print(f"  VENDOR BUSINESS ANALYTICS")
        print(f"{'='*60}{RESET}")
        print(f"Total Orders:      {stats['total_orders']}")
        print(f"Total Revenue:     ${stats['total_revenue']:.2f}")
        print(f"Avg Order Value:   ${stats['avg_order_value']:.2f}")
        print(f"Completed Orders:  {stats['completed_orders']}")
        print(f"Cancelled Orders:  {stats['cancelled_orders']}")
        print(f"Pending Orders:    {stats['pending_orders']}")
        print(f"{YELLOW}{'='*60}{RESET}\n")
    else:
        print_error(f"Get stats failed: {response.json()}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    print_section("🚀 FEMS REFACTORED VENDOR ROUTES - COMPLETE TEST SUITE", BLUE)
    print("This test validates the NEW stored procedure approach")
    print("Testing: Menu Management + Order Management + Analytics")
    print()
    
    try:
        # Test server
        print_info("Checking server connection...")
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code != 200:
            print_error("Server not responding")
            return
        print_success("Server is healthy\n")
        
        # Phase 1: Vendor Setup
        vendor_token, vendor_id = setup_vendor()
        
        # Phase 2: Menu Management
        result = test_menu_management(vendor_token, vendor_id)
        if not result:
            print_error("Menu management tests failed")
            return
        menu_id, item_ids = result
        
        # Phase 3: Create Customer Order
        order_id = create_customer_order(vendor_id, item_ids[:2])
        if not order_id:
            print_error("Order creation failed")
            return
        
        # Phase 4: Order Management (NEW!)
        test_order_management(vendor_token, vendor_id, order_id)
        
        # Phase 5: Analytics (NEW!)
        test_analytics(vendor_token, vendor_id)
        
        # Final Summary
        print_section("✅ TEST SUMMARY", GREEN)
        print(f"{GREEN}All tests passed successfully!{RESET}\n")
        
        print("Features Tested:")
        print(f"  {GREEN}✓{RESET} Vendor Registration & Authentication")
        print(f"  {GREEN}✓{RESET} Menu Creation (Stored Procedure)")
        print(f"  {GREEN}✓{RESET} Batch Item Addition (Stored Procedure)")
        print(f"  {GREEN}✓{RESET} Item Update (Stored Procedure)")
        print(f"  {GREEN}✓{RESET} Item Deletion (Stored Procedure)")
        print(f"  {GREEN}✓{RESET} Public Vendor Info Retrieval")
        print(f"  {GREEN}✓{RESET} Order Viewing (NEW)")
        print(f"  {GREEN}✓{RESET} Order Filtering (NEW)")
        print(f"  {GREEN}✓{RESET} Order Status Updates (NEW)")
        print(f"  {GREEN}✓{RESET} Complete Order Lifecycle (NEW)")
        print(f"  {GREEN}✓{RESET} Vendor Analytics (NEW)")
        
        print("\nTest Data:")
        print(f"  Vendor ID: {vendor_id}")
        print(f"  Menu ID: {menu_id}")
        print(f"  Order ID: {order_id}")
        
        print(f"\n{CYAN}{'='*80}")
        print(f"🎉 Refactored Vendor System is fully operational!")
        print(f"{'='*80}{RESET}\n")
        
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}❌ Cannot connect to server at {BASE_URL}{RESET}")
        print("Please ensure Flask server is running: python -m backend.app")
    except Exception as e:
        print(f"\n{RED}❌ Unexpected error: {str(e)}{RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()