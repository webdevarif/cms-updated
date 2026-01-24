"""
Test configuration for accounts app.
"""
import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Configure pytest settings
pytest_plugins = [
    'apps.accounts.tests.fixtures',
]

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.api = pytest.mark.api
pytest.mark.model = pytest.mark.model
pytest.mark.service = pytest.mark.service
