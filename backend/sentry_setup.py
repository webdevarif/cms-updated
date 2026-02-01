#!/usr/bin/env python3
"""
Sentry Setup Helper for Digital Farmers CMS

This script helps set up Sentry monitoring for the Django application.
It validates the configuration and provides testing utilities.
"""

import logging
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    import sentry_sdk
    from django.conf import settings
    from django.core.management import execute_from_command_line
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory with Django activated")
    sys.exit(1)


def check_sentry_configuration():
    """Check Sentry configuration and provide recommendations."""
    print("🔍 Checking Sentry Configuration")
    print("=" * 50)

    # Check environment variables
    sentry_dsn = os.getenv("SENTRY_DSN")
    sentry_env = os.getenv("SENTRY_ENVIRONMENT", "development")
    sentry_release = os.getenv("SENTRY_RELEASE", "1.0.0")

    print(f"📊 SENTRY_DSN: {'✅ Set' if sentry_dsn else '❌ Not set'}")
    print(f"🌍 SENTRY_ENVIRONMENT: {sentry_env}")
    print(f"🏷️  SENTRY_RELEASE: {sentry_release}")

    if not sentry_dsn:
        print("\n❌ SENTRY_DSN is not set!")
        print("Please set SENTRY_DSN in your environment or .env file:")
        print("SENTRY_DSN=https://your-dsn@sentry.io/project-id")
        return False

    return True


def test_sentry_integration():
    """Test Sentry integration by sending a test event."""
    print("\n🧪 Testing Sentry Integration")
    print("=" * 50)

    try:
        # Test message
        sentry_sdk.capture_message("Sentry integration test - Digital Farmers CMS")
        print("✅ Test message sent to Sentry")

        # Test exception
        try:
            raise ValueError("This is a test exception for Sentry")
        except Exception:
            sentry_sdk.capture_exception()
            print("✅ Test exception sent to Sentry")

        return True

    except Exception as e:
        print(f"❌ Failed to send test to Sentry: {e}")
        return False


def check_performance_monitoring():
    """Check performance monitoring configuration."""
    print("\n⚡ Performance Monitoring Check")
    print("=" * 50)

    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))

    print(f"📈 Traces Sample Rate: {traces_sample_rate * 100}%")
    print(f"👤 Profiles Sample Rate: {profiles_sample_rate * 100}%")

    if traces_sample_rate > 0.5:
        print("⚠️  High traces sample rate - consider reducing for production")

    if profiles_sample_rate > 0.1:
        print("⚠️  High profiles sample rate - consider reducing for production")

    print("✅ Performance monitoring is configured")


def setup_django():
    """Set up Django environment for testing."""
    print("\n🔧 Setting up Django Environment")
    print("=" * 50)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.base")

    try:
        import django
        from django.core.wsgi import get_wsgi_application

        django.setup()
        print("✅ Django environment set up successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to set up Django: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 Digital Farmers CMS - Sentry Setup Helper")
    print("=" * 50)

    # Check configuration
    if not check_sentry_configuration():
        print("\n❌ Please fix the configuration issues above")
        sys.exit(1)

    # Set up Django
    if not setup_django():
        print("\n❌ Django setup failed")
        sys.exit(1)

    # Check performance monitoring
    check_performance_monitoring()

    # Test integration
    if test_sentry_integration():
        print("\n✅ Sentry integration test completed successfully!")
        print("📊 Check your Sentry dashboard for the test events")
    else:
        print("\n❌ Sentry integration test failed")
        sys.exit(1)

    print("\n🎯 Sentry Setup Complete!")
    print("=" * 50)
    print("📋 Next Steps:")
    print("1. Verify events appear in your Sentry dashboard")
    print("2. Adjust sample rates for production if needed")
    print("3. Set up alerts and notifications in Sentry")
    print("4. Configure performance monitoring dashboards")


if __name__ == "__main__":
    main()
