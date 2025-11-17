# # import http.client
# # import json

# # # Use HTTPConnection because Flask is running on HTTP, not HTTPS
# # conn = http.client.HTTPConnection("localhost", 5000)

# # headersList = {
# #     "Accept": "*/*",
# #     "User-Agent": "Thunder Client (https://www.thunderclient.com)",
# #     "Content-Type": "application/json"
# # }

# # # Payload for registration
# # payload = json.dumps({
# #     "email": "test@example.com",
# #     "password": "password123"
# # })

# # # Make POST request to /api/register
# # conn.request("POST", "/api/register", payload, headersList)

# # # Get response
# # response = conn.getresponse()
# # result = response.read()

# # # Print status code and JSON response
# # print("Status:", response.status)
# # print("Response JSON:", result.decode("utf-8"))


# import requests

# BASE_URL = "http://127.0.0.1:5000"

# # ======== 1. REGISTER USER ========
# def test_register():
#     url = f"{BASE_URL}/api/register"
#     payload = {
#         "email": "test8@example.com",
#         "password": "password789"
#     }
#     response = requests.post(url, json=payload)
#     print("=== REGISTER ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())
#     return response.json().get("verification_code")

# # ======== 2. VERIFY EMAIL ========
# def test_verify_email(code):
#     url = f"{BASE_URL}/api/verify-email"
#     payload = {
#         "email": "test8@example.com",
#         "code": code
#     }
#     response = requests.post(url, json=payload)
#     print("=== VERIFY EMAIL ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # ======== 3. LOGIN ========
# def test_login():
#     url = f"{BASE_URL}/api/login"
#     payload = {
#         "email": "test8@example.com",
#         "password": "password123"
#     }
#     response = requests.post(url, json=payload)
#     print("=== LOGIN ===")
#     print("Status:", response.status_code)
#     data = response.json()
#     print("Response:", data)
#     token = data.get("token")
#     return token

# # ======== 4. PROFILE ========
# def test_profile(token):
#     url = f"{BASE_URL}/api/profile"
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(url, headers=headers)
#     print("=== PROFILE ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # ======== 5. COMPLETE PROFILE ========
# def test_complete_profile(token):
#     url = f"{BASE_URL}/api/complete-profile"
#     headers = {"Authorization": f"Bearer {token}"}
#     payload = {
#         "full_name": "John Doe",
#         "phone": "1234567890",
#         "role": "vendor",
#         "vendor_name": "John's Cafe",
#         "location": "Downtown"
#     }
#     response = requests.post(url, json=payload, headers=headers)
#     print("=== COMPLETE PROFILE ===")
#     print("Status:", response.status_code)
#     print("Response:", response.json())

# # ======== RUN ALL TESTS ========
# if __name__ == "__main__":
#     verification_code = test_register()
#     if verification_code:
#         test_verify_email(verification_code)
#         token = test_login()
#         if token:
#             test_profile(token)
#             test_complete_profile(token)


import requests

BASE_URL = "http://127.0.0.1:5000"

# -------------------------------
# 1️⃣ REGISTER
# -------------------------------
def test_register():
    url = f"{BASE_URL}/api/register"
    payload = {
        "email": "test10@example.com",
        "password": "password789"
    }
    response = requests.post(url, json=payload)
    data = response.json()
    print("=== REGISTER ===")
    print("Status:", response.status_code)
    print("Response:", data)
    return data.get("verification_code")  # return verification code

# -------------------------------
# 2️⃣ VERIFY EMAIL
# -------------------------------
def test_verify_email(verification_code):
    url = f"{BASE_URL}/api/verify-email"
    payload = {
        "email": "test10@example.com",
        "code": verification_code
    }
    response = requests.post(url, json=payload)
    print("=== VERIFY EMAIL ===")
    print("Status:", response.status_code)
    print("Response:", response.json())

# -------------------------------
# 3️⃣ LOGIN
# -------------------------------
def test_login():
    url = f"{BASE_URL}/api/login"
    payload = {
        "email": "test10@example.com",
        "password": "password789"
    }
    response = requests.post(url, json=payload)
    data = response.json()
    print("=== LOGIN ===")
    print("Status:", response.status_code)
    print("Response:", data)
    if response.status_code == 200:
        return data["token"]  # return JWT token
    return None

# -------------------------------
# 4️⃣ COMPLETE PROFILE (vendor)
# -------------------------------
def test_complete_profile(token):
    url = f"{BASE_URL}/api/complete-profile"
    payload = {
        "full_name": "george Vendor",
        "phone": "1234567890",
        "role": "vendor",
        "vendor_name": "george Cafe",
        "location": "New York"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print("=== COMPLETE PROFILE ===")
    print("Status:", response.status_code)
    print("Response:", data)
    vendor_id = data.get("vendor", {}).get("id")
    return vendor_id  # return vendor id for menu creation

# -------------------------------
# 5️⃣ CREATE MENU
# -------------------------------
def test_create_menu(token, vendor_id):
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu"
    payload = {"title": "Breakfast Menu"}
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    print("=== CREATE MENU ===")
    print("Status:", response.status_code)
    print("Response:", data)
    menu_id = data.get("menu", {}).get("id")
    return menu_id

# -------------------------------
# 6️⃣ ADD MENU ITEMS
# -------------------------------
def test_add_menu_items(token, vendor_id, menu_id):
    url = f"{BASE_URL}/api/vendors/{vendor_id}/menu/{menu_id}/items"
    payload = [
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
    ]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, json=payload, headers=headers)
    print("=== ADD MENU ITEMS ===")
    print("Status:", response.status_code)
    print("Response:", response.json())

# -------------------------------
# 7️⃣ GET VENDOR INFO
# -------------------------------
def test_get_vendor(vendor_id):
    url = f"{BASE_URL}/api/vendors/{vendor_id}"
    response = requests.get(url)
    print("=== GET VENDOR INFO ===")
    print("Status:", response.status_code)
    print("Response:", response.json())

# -------------------------------
# RUN FULL FLOW
# -------------------------------
if __name__ == "__main__":
    verification_code = test_register()
    if verification_code:
        test_verify_email(verification_code)
        token = test_login()
        if token:
            vendor_id = test_complete_profile(token)
            if vendor_id:
                menu_id = test_create_menu(token, vendor_id)
                if menu_id:
                    test_add_menu_items(token, vendor_id, menu_id)
                    test_get_vendor(vendor_id)
