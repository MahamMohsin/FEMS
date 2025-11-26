# vendor_test.py
"""
End-to-end vendor tests for FEMS refactored vendor routes.

Run sequence:
1. Apply SQL fixes in Supabase (run the three CREATE OR REPLACE FUNCTION statements).
2. Restart Flask server (python -m backend.app).
3. Run: python vendor_test.py
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import requests

BASE_URL = "http://127.0.0.1:5000"

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


def print_section(title: str, color: str = BLUE) -> None:
    print(f"\n{color}{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}{RESET}\n")


def print_success(msg: str) -> None:
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg: str) -> None:
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg: str) -> None:
    print(f"{CYAN}ℹ {msg}{RESET}")


def print_highlight(msg: str) -> None:
    print(f"{YELLOW}➤ {msg}{RESET}")


def extract_vendor_id_from_profile(profile_json: Dict) -> Optional[int]:
    """Extract vendor id from common profile shapes."""
    user = profile_json.get("user") or profile_json.get("profile") or profile_json
    if isinstance(user, dict):
        vendor_obj = user.get("vendor")
        if isinstance(vendor_obj, dict) and vendor_obj.get("id"):
            return int(vendor_obj.get("id"))
        if user.get("vendor_id"):
            return int(user.get("vendor_id"))
        vendors_list = user.get("vendors")
        if isinstance(vendors_list, list) and vendors_list:
            first_vendor = vendors_list[0]
            if isinstance(first_vendor, dict) and first_vendor.get("id"):
                return int(first_vendor.get("id"))
    return None


def setup_vendor() -> Tuple[str, int]:
    """Register or login vendor and ensure a vendor record exists; return (token, vendor_id)."""
    print_section("🏪 VENDOR SETUP", MAGENTA)

    email = "pizzapalace@test.com"
    password = "pizza123"

    print_info("Registering vendor...")
    resp = requests.post(f"{BASE_URL}/api/register", json={"email": email, "password": password})

    if resp.status_code == 409:
        print_highlight("Vendor already exists, logging in...")
        login_resp = requests.post(f"{BASE_URL}/api/login", json={"email": email, "password": password})
        login_resp.raise_for_status()
        token = login_resp.json().get("token")
        profile_resp = requests.get(f"{BASE_URL}/api/profile", headers={"Authorization": f"Bearer {token}"})
        profile_resp.raise_for_status()
        vendor_id = extract_vendor_id_from_profile(profile_resp.json())
        if vendor_id:
            print_success(f"Using existing vendor account (vendor_id={vendor_id})")
            return token, vendor_id
        # If profile had no vendor data, call complete-profile to create vendor
        print_info("No vendor in profile; completing profile to create vendor entry...")
        complete_resp = requests.post(
            f"{BASE_URL}/api/complete-profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "full_name": "Pizza Palace Owner",
                "phone": "1234567890",
                "role": "vendor",
                "vendor_name": "Pizza Palace",
                "location": "Campus Main Street",
            },
        )
        complete_resp.raise_for_status()
        vendor_obj = complete_resp.json().get("vendor") or complete_resp.json()
        vendor_id = vendor_obj.get("id")
        if not vendor_id:
            raise SystemExit("complete-profile did not return vendor id")
        print_success(f"Vendor profile created (ID: {vendor_id})")
        return token, int(vendor_id)

    if resp.status_code in (200, 201):
        data = resp.json()
        verification_code = data.get("verification_code")
        if verification_code:
            print_info("Verifying email...")
            vresp = requests.post(f"{BASE_URL}/api/verify-email", json={"email": email, "code": verification_code})
            vresp.raise_for_status()
            print_success("Email verified")

        login_resp = requests.post(f"{BASE_URL}/api/login", json={"email": email, "password": password})
        login_resp.raise_for_status()
        token = login_resp.json().get("token")

        complete_resp = requests.post(
            f"{BASE_URL}/api/complete-profile",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "full_name": "Pizza Palace Owner",
                "phone": "1234567890",
                "role": "vendor",
                "vendor_name": "Pizza Palace",
                "location": "Campus Main Street",
            },
        )
        complete_resp.raise_for_status()
        vendor_obj = complete_resp.json().get("vendor") or complete_resp.json()
        vendor_id = vendor_obj.get("id")
        if not vendor_id:
            raise SystemExit("complete-profile failed to return vendor id")
        print_success(f"Vendor profile created (ID: {vendor_id})")
        return token, int(vendor_id)

    print_error(f"Registration error: {resp.status_code} {resp.text}")
    raise SystemExit(1)


def test_menu_management(token: str, vendor_id: int) -> Tuple[int, List[int]]:
    """Create menu (if needed), add items, update an item, delete an item; returns (menu_id, item_ids)."""
    print_section("📋 MENU MANAGEMENT TESTS", CYAN)

    print_highlight("Test 1: Create Menu")
    resp = requests.post(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Main Menu"},
    )

    if resp.status_code == 201:
        menu_id = resp.json()["menu"]["id"]
        print_success(f"Menu created (ID: {menu_id})")
    elif resp.status_code == 400 and "already exists" in resp.json().get("error", ""):
        print_info("Menu already exists, fetching vendor to obtain existing menu id")
        vendor_resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}")
        vendor_resp.raise_for_status()
        vendor_data = vendor_resp.json()["vendor"]
        menu_id = vendor_data.get("menu", {}).get("id")
        if not menu_id:
            raise SystemExit("Could not determine existing menu id")
        print_success(f"Using existing menu (ID: {menu_id})")
    else:
        print_error(f"Menu creation failed: {resp.status_code} {resp.text}")
        raise SystemExit(1)

    print_highlight("Test 2: Add Menu Items (Batch)")
    items_payload = [
        {"name": "Margherita Pizza", "description": "Classic tomato and mozzarella", "price": 12.99, "available": True, "preparation_time_minutes": 20},
        {"name": "Pepperoni Pizza", "description": "Loaded with pepperoni", "price": 14.99, "available": True, "preparation_time_minutes": 20},
        {"name": "Coke", "description": "Refreshing soda", "price": 2.99, "available": True, "preparation_time_minutes": 2},
    ]
    add_resp = requests.post(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json=items_payload,
    )
    add_resp.raise_for_status()
    item_ids = [int(item["id"]) for item in add_resp.json()["items"]]
    print_success(f"Added {len(item_ids)} items, IDs: {item_ids}")

    print_highlight("Test 3: Update Menu Item")
    upd_resp = requests.put(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_ids[0]}",
        headers={"Authorization": f"Bearer {token}"},
        json={"price": 13.99, "description": "Classic tomato and fresh mozzarella"},
    )
    upd_resp.raise_for_status()
    print_success(f"Updated item: {upd_resp.json()['item']['name']} - ${upd_resp.json()['item']['price']}")

    print_highlight("Test 4: Delete Menu Item")
    del_resp = requests.delete(
        f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items/{item_ids[2]}",
        headers={"Authorization": f"Bearer {token}"},
    )
    del_resp.raise_for_status()
    print_success(f"Deleted item: {del_resp.json()['deleted_item']['name']}")

    print_highlight("Test 5: Get Vendor Info (Public)")
    vinfo_resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}")
    vinfo_resp.raise_for_status()
    vinfo = vinfo_resp.json()["vendor"]
    print_success(f"Vendor: {vinfo.get('vendor_name')}, Location: {vinfo.get('location')}")
    if vinfo.get("menu"):
        print_info(f"Menu items count: {len(vinfo['menu'].get('items', []))}")

    return menu_id, item_ids


def create_customer_order(vendor_id: int, item_ids: List[int]) -> Optional[int]:
    print_section("👤 CUSTOMER ORDER CREATION", BLUE)
    email = "student@test.com"
    password = "student123"

    print_info("Registering customer...")
    r = requests.post(f"{BASE_URL}/api/register", json={"email": email, "password": password})
    if r.status_code == 409:
        login = requests.post(f"{BASE_URL}/api/login", json={"email": email, "password": password})
        login.raise_for_status()
        token = login.json().get("token")
    else:
        data = r.json()
        code = data.get("verification_code")
        if code:
            requests.post(f"{BASE_URL}/api/verify-email", json={"email": email, "code": code})
        login = requests.post(f"{BASE_URL}/api/login", json={"email": email, "password": password})
        login.raise_for_status()
        token = login.json().get("token")
        requests.post(
            f"{BASE_URL}/api/complete-profile",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "John Student", "phone": "9876543210", "role": "customer"},
        )

    pickup_time = (datetime.utcnow() + timedelta(hours=4)).isoformat()
    order_payload = {
        "vendor_id": vendor_id,
        "pickup_time": pickup_time,
        "pickup_or_delivery": "pickup",
        "order_notes": "Extra cheese please",
        "items": [{"menu_item_id": item_ids[0], "quantity": 2}, {"menu_item_id": item_ids[1], "quantity": 1}],
    }
    order_resp = requests.post(f"{BASE_URL}/api/customer/orders", headers={"Authorization": f"Bearer {token}"}, json=order_payload)
    order_resp.raise_for_status()
    order_json = order_resp.json()
    order_id = order_json["order"]["order_id"]
    print_success(f"Order placed (ID: {order_id}, Total: ${order_json['order']['total_amount']})")
    return int(order_id)


def test_order_management(token: str, vendor_id: int, order_id: int) -> None:
    print_section("📦 ORDER MANAGEMENT TESTS (NEW FEATURE!)", MAGENTA)

    print_highlight("Test 1: View All Orders")
    resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}/orders", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    data = resp.json()
    print_success(f"Vendor orders total: {data.get('total')}")

    print_highlight("Test 2: View Pending Orders")
    resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}/orders?status=pending", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    print_success(f"Pending orders: {resp.json().get('total')}")

    print_highlight("Test 3: View Order Details")
    resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    order = resp.json().get("order", {})
    print_success(f"Order details retrieved. Status: {order.get('status')}")

    print_highlight("Test 4: Accept Order")
    ready_time = (datetime.utcnow() + timedelta(hours=3, minutes=45)).isoformat()
    resp = requests.put(f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status", headers={"Authorization": f"Bearer {token}"}, json={"status": "accepted", "estimated_ready_at": ready_time})
    resp.raise_for_status()
    print_success(f"Order accepted: {resp.json()['order']['old_status']} -> {resp.json()['order']['new_status']}")

    print_highlight("Test 5: Start Preparing")
    resp = requests.put(f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status", headers={"Authorization": f"Bearer {token}"}, json={"status": "preparing"})
    resp.raise_for_status()
    print_success("Order preparing")

    print_highlight("Test 6: Mark Ready for Pickup")
    resp = requests.put(f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status", headers={"Authorization": f"Bearer {token}"}, json={"status": "ready"})
    resp.raise_for_status()
    print_success("Order marked ready")

    print_highlight("Test 7: Mark as Completed")
    resp = requests.put(f"{BASE_URL}/api/vendors/{vendor_id}/orders/{order_id}/status", headers={"Authorization": f"Bearer {token}"}, json={"status": "completed"})
    resp.raise_for_status()
    print_success("Order marked completed")


def test_analytics(token: str, vendor_id: int) -> None:
    print_section("📊 ANALYTICS TESTS", CYAN)
    resp = requests.get(f"{BASE_URL}/api/vendors/{vendor_id}/stats", headers={"Authorization": f"Bearer {token}"})
    resp.raise_for_status()
    stats = resp.json().get("stats", {})
    print_success("Analytics retrieved")
    print(f"Total Orders: {stats.get('total_orders')}, Total Revenue: {stats.get('total_revenue')}")


def main() -> None:
    print_section("🚀 FEMS VENDOR ROUTES - TEST SUITE", BLUE)
    try:
        h = requests.get(f"{BASE_URL}/api/health")
        h.raise_for_status()
        print_success("Server healthy")

        token, vendor_id = setup_vendor()
        menu_id, item_ids = test_menu_management(token, vendor_id)
        order_id = create_customer_order(vendor_id, item_ids[:2])
        test_order_management(token, vendor_id, order_id)
        test_analytics(token, vendor_id)

        print_section("✅ TEST SUMMARY", GREEN)
        print_success("All tests completed. Inspect outputs above for details.")
        print(f"Vendor ID: {vendor_id}, Menu ID: {menu_id}, Order ID: {order_id}")
    except requests.exceptions.RequestException as e:
        print_error(f"HTTP error: {e}")
    except Exception as exc:
        print_error(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()
