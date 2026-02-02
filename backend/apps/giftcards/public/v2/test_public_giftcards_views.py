"""
Tests for gift cards API views.
"""

import json
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from ...accounts.tests.factories import UserFactory
from ...ecommerce.models import Order
from ...stores.tests.factories import StoreFactory
from ..models import GiftCard, GiftCardHistory


class GiftCardViewSetTestCase(APITestCase):
    """Test cases for GiftCardViewSet."""

    def setUp(self):
        """Set up test data."""
        self.store = StoreFactory()
        self.user = UserFactory()
        self.now = timezone.now()
        self.client.force_authenticate(user=self.user)

        # Create a test gift card
        self.gift_card = GiftCard.objects.create(
            store=self.store,
            code="TEST12345678",
            initial_balance=100.00,
            current_balance=100.00,
            currency="USD",
            gift_card_type="digital",
            status="active",
            expires_at=self.now + timedelta(days=365),
            created_by=self.user,
        )

        # URLs
        self.list_url = reverse("v2:giftcard-list")
        self.detail_url = reverse("v2:giftcard-detail", args=[self.gift_card.id])
        self.redeem_url = reverse("v2:giftcard-redeem")
        self.balance_url = reverse("v2:giftcard-balance")
        self.activate_url = reverse("v2:giftcard-activate", args=[self.gift_card.id])
        self.void_url = reverse("v2:giftcard-void", args=[self.gift_card.id])
        self.history_url = reverse("v2:giftcard-history", args=[self.gift_card.id])

    def test_list_gift_cards(self):
        """Test listing gift cards with filtering."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["code"], "TEST12345678")

        # Test filtering by status
        response = self.client.get(f"{self.list_url}?status=expired")
        self.assertEqual(len(response.data["results"]), 0)

    def test_retrieve_gift_card(self):
        """Test retrieving a single gift card."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], "TEST12345678")

    def test_create_gift_card(self):
        """Test creating a new gift card."""
        data = {
            "initial_balance": "50.00",
            "currency": "USD",
            "gift_card_type": "physical",
            "expires_at": (self.now + timedelta(days=365)).isoformat(),
            "recipient_email": "test@example.com",
            "message": "Test message",
        }

        with patch(
            "apps.giftcards.services.GiftCardService._generate_code",
            return_value="NEWCODE123456",
        ):
            response = self.client.post(self.list_url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["code"], "NEWCODE123456")
            self.assertEqual(response.data["initial_balance"], "50.00")

    def test_redeem_gift_card(self):
        """Test redeeming a gift card."""
        order = Order.objects.create(
            store=self.store, total_amount=30.00, status="pending", created_by=self.user
        )

        data = {
            "code": "TEST12345678",
            "amount": "30.00",
            "order_id": order.id,
            "method": "online",
        }

        response = self.client.post(self.redeem_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["current_balance"], "70.00")

        # Verify the gift card was updated
        self.gift_card.refresh_from_db()
        self.assertEqual(self.gift_card.current_balance, 70.00)

    def test_check_balance(self):
        """Test checking a gift card balance."""
        response = self.client.get(f"{self.balance_url}?code=TEST12345678")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["balance"], "100.00")
        self.assertEqual(response.data["currency"], "USD")

    def test_activate_gift_card(self):
        """Test activating a gift card."""
        # Create an inactive gift card
        inactive_card = GiftCard.objects.create(
            store=self.store,
            code="INACTIVE123",
            initial_balance=50.00,
            current_balance=50.00,
            currency="USD",
            gift_card_type="digital",
            status="inactive",
            created_by=self.user,
        )

        activate_url = reverse("v2:giftcard-activate", args=[inactive_card.id])
        response = self.client.post(activate_url, {"notes": "Activated via API"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "active")

    def test_void_gift_card(self):
        """Test voiding a gift card."""
        data = {"reason": "Test void", "notes": "Voided via API"}

        response = self.client.post(self.void_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "voided")

    def test_gift_card_history(self):
        """Test retrieving gift card history."""
        # Add some history
        GiftCardHistory.objects.create(
            gift_card=self.gift_card,
            action="created",
            amount=100.00,
            created_by=self.user,
        )

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["action"], "created")

    def test_rate_limiting(self):
        """Test rate limiting for gift card operations."""
        # Test balance check rate limiting
        for _ in range(5):  # Should be under default limit
            response = self.client.get(f"{self.balance_url}?code=TEST12345678")
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The next request should be rate limited
        response = self.client.get(f"{self.balance_url}?code=TEST12345678")
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class GiftCardHistoryViewSetTestCase(APITestCase):
    """Test cases for GiftCardHistoryViewSet."""

    def setUp(self):
        """Set up test data."""
        self.store = StoreFactory()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

        # Create a test gift card with history
        self.gift_card = GiftCard.objects.create(
            store=self.store,
            code="HISTORY123",
            initial_balance=100.00,
            current_balance=100.00,
            currency="USD",
            gift_card_type="digital",
            status="active",
            created_by=self.user,
        )

        # Add some history
        self.history = [
            GiftCardHistory.objects.create(
                gift_card=self.gift_card,
                action="created",
                amount=100.00,
                created_by=self.user,
                metadata={"test": "data"},
            ),
            GiftCardHistory.objects.create(
                gift_card=self.gift_card,
                action="redeemed",
                amount=30.00,
                created_by=self.user,
                metadata={"order_id": "123"},
            ),
        ]

        # URLs
        self.list_url = reverse("v2:giftcardhistory-list")

    def test_list_history(self):
        """Test listing gift card history with filtering."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Test filtering by action
        response = self.client.get(f"{self.list_url}?action=redeemed")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["action"], "redeemed")

        # Test filtering by gift card ID
        response = self.client.get(f"{self.list_url}?gift_card_id={self.gift_card.id}")
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_history(self):
        """Test retrieving a single history entry."""
        history = self.history[0]
        url = reverse("v2:giftcardhistory-detail", args=[history.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "created")
        self.assertEqual(response.data["amount"], "100.00")
