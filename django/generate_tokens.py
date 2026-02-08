#!/usr/bin/env python
"""
Generate JWT tokens for the admin user.
Run this script to get new access and refresh tokens.
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
sys.path.append(os.path.dirname(__file__))
django.setup()

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model


def main():
    User = get_user_model()
    try:
        # Try to find admin user by email first
        user = User.objects.filter(email="admin@example.com").first()
        if not user:
            # If not found, get any user
            user = User.objects.first()
        if not user:
            # If no users exist, create admin user
            user = User.objects.create_superuser("admin", "admin@example.com", "admin123")
            print("✅ Admin user created")
        else:
            print("✅ Found existing user")
    except Exception as e:
        print(f"❌ Error finding user: {e}")
        return

    print(f"User: ID={user.id}, Email={user.email}, Username={user.username}")

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    print("\n🎯 JWT TOKENS GENERATED")
    print("=" * 60)
    print("\n📋 ACCESS TOKEN (use in Authorization header):")
    print(f"Bearer {access_token}")
    print("\n🔄 REFRESH TOKEN (use for /auth/jwt/refresh/):")
    print(refresh_token)
    print("\n📝 USAGE:")
    print("1. Copy the access token")
    print("2. Add to request headers:")
    print("   Authorization: Bearer <access_token>")
    print("\n3. When access token expires, refresh it:")
    print("   POST /auth/jwt/refresh/")
    print('   Body: {"refresh": "<refresh_token>"}')


if __name__ == "__main__":
    main()
