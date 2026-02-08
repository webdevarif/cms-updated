#!/usr/bin/env python
"""
Test JWT authentication with new tokens
"""
import json

import requests


def test_jwt_auth():
    base_url = "http://127.0.0.1:8000"

    # New access token
    access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwMzcxNzA0LCJpYXQiOjE3NzAzNzE0MDQsImp0aSI6Ijk1YjU5MDhmMDhiYTQyMTk4N2ZlZjJmYWIzOGM5Nzc1IiwidXNlcl9pZCI6IjEifQ.6YW0wA-_eJMPO-tlTZIhD1dLS_y5e_-2xGuRpkHHlV8"

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"}

    print("🧪 Testing JWT Authentication")
    print("=" * 50)

    # Test access token
    try:
        response = requests.get(f"{base_url}/auth/users/me/", headers=headers)
        print(f"✅ Access token test - Status: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f'   User: {user_data.get("username", "unknown")}')
        else:
            print(f"   Error: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Access token error: {e}")

    # Test refresh token
    refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc3MDQ1NzgwNCwiaWF0IjoxNzcwMzcxNDA0LCJqdGkiOiI2NzRhZGQ3MTg3NTc0YzdkOTIxNDkzYjQyNWE1ZGMyMCIsInVzZXJfaWQiOiIxIn0.nCv3vf-cAt6sqE3VzHBYGM93LrALELH9PrUrqlrzGM8"

    refresh_data = {"refresh": refresh_token}

    try:
        response = requests.post(
            f"{base_url}/auth/jwt/refresh/",
            json=refresh_data,
            headers={"Content-Type": "application/json"},
        )
        print(f"✅ Refresh token test - Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Refresh successful!")
        else:
            print(f"   ❌ Refresh failed: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Refresh token error: {e}")


if __name__ == "__main__":
    test_jwt_auth()
