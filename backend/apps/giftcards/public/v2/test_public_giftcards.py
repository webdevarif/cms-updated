"""
Public gift cards API tests - endpoint-focused only.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

User = get_user_model()


class PublicGiftCardsAPITests(APITestCase):
    """Test public gift cards endpoints - read-only only."""

    def setUp(self):
        """Set up test data"""
        from apps.giftcards.models.giftcards import GiftCard
        from apps.stores.models import Store

        self.store = Store.objects.create(name="Test Store", slug="test-store", owner=None)

        self.user = User.objects.create_user(email="test@example.com", password="testpass123")

        # Create an active gift card
        self.gift_card = GiftCard.objects.create(
            store=self.store,
            created_by=self.user,
            gift_card_type="digital",
            initial_balance=Decimal("100.00"),
            currency="USD",
            recipient_name="John Doe",
            recipient_email="john@example.com",
            status="active",
        )

        # Create an inactive gift card (should not be visible)
        self.inactive_card = GiftCard.objects.create(
            store=self.store,
            created_by=self.user,
            gift_card_type="digital",
            initial_balance=Decimal("50.00"),
            currency="USD",
            status="inactive",
        )

        self.client = APIClient()

    def test_list_active_gift_cards(self):
        """Test listing active gift cards"""
        url = reverse("public-gift-cards-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["code"], self.gift_card.code)

    def test_retrieve_active_gift_card(self):
        """Test retrieving an active gift card"""
        url = reverse("public-gift-cards-detail", kwargs={"pk": self.gift_card.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], self.gift_card.code)
        self.assertEqual(response.data["current_balance"], "100.00")
        self.assertTrue(response.data["is_redeemable"])
        self.assertFalse(response.data["is_expired"])

    def test_check_gift_card_balance(self):
        """Test checking gift card balance"""
        url = reverse("public-gift-cards-balance")
        response = self.client.get(url, {"code": self.gift_card.code})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["balance"], "100.00")
        self.assertEqual(response.data["currency"], "USD")
        self.assertFalse(response.data["is_expired"])
        self.assertEqual(response.data["status"], "active")

    def test_check_gift_card_by_url(self):
        """Test checking gift card by code in URL"""
        url = f"/api/public/gift-cards/check/{self.gift_card.code}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["code"], self.gift_card.code)
        self.assertEqual(response.data["current_balance"], "100.00")

    def test_inactive_cards_not_visible(self):
        """Test that inactive cards are not visible"""
        url = reverse("public-gift-cards-list")
        response = self.client.get(url)

        # Should only see the active card
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "active")

    def test_retrieve_inactive_card(self):
        """Test that inactive cards cannot be retrieved"""
        url = reverse("public-gift-cards-detail", kwargs={"pk": self.inactive_card.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_card_balance(self):
        """Test checking balance for non-existent card"""
        url = reverse("public-gift-cards-balance")
        response = self.get(url, {"code": "NONEXISTENT"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_nonexistent_card_by_url(self):
        """Test checking non-existent card by URL"""
        url = "/api/public/gift-cards/check/NONEXISTENT/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_gift_cards(self):
        """Test searching gift cards"""
        url = reverse("public-gift-cards-list")
        response = self.client.get(url, {"search": "john"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["recipient_name"], "John Doe")

    def test_filter_by_type(self):
        """Test filtering gift cards by type"""
        url = reverse("public-gift-cards-list")
        response = self.client.get(url, {"gift_card_type": "digital"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["gift_card_type"], "digital")

    def test_ordering_gift_cards(self):
        """Test ordering gift cards"""
        url = reverse("public-gift-cards-list")
        response = self.client.get(url, {"ordering": "current_balance"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_expired_card_not_redeemable(self):
        """Test that expired cards are not redeemable"""
        # Create an expired card
        import datetime

        from apps.giftcards.models.giftcards import GiftCard
        from django.utils import timezone

        expired_card = GiftCard.objects.create(
            store=self.store,
            created_by=self.user,
            gift_card_type="digital",
            initial_balance=Decimal("25.00"),
            expires_at=timezone.now() - datetime.timedelta(days=1),
            status="active",
        )

        url = reverse("public-gift_cards-detail", kwargs={"pk": expired_card.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_expired"])
        self.assertFalse(response.data["is_redeemable"])

    def test_zero_balance_card_not_redeemable(self):
        """Test that zero balance cards are not redeemable"""
        # Create a card with zero balance
        from apps.giftcards.models.giftcards import GiftCard

        zero_card = GiftCard.objects.create(
            store=self.store,
            created_by=self.user,
            gift_card_type="digital",
            initial_balance=Decimal("0.00"),
            current_balance=Decimal("0.00"),
            status="active",
        )

        url = reverse("public-gift-cards-detail", kwargs={"pk": zero_card.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_redeemable"])

    def test_read_only_serializer_fields(self):
        """Test that serializer fields are read-only"""
        url = reverse("public-gift-cards-detail", kwargs={"pk": self.gift_card.id})

        # Try to update via POST (should fail)
        response = self.client.post(url, {"current_balance": "50.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to update via PATCH (should fail)
        response = self.client.patch(url, {"current_balance": "50.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Try to delete (should fail)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_balance_endpoint_without_code(self):
        """Test balance endpoint without code parameter"""
        url = reverse("public-gift-cards-balance")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "code parameter is required")

    def test_check_endpoint_without_code(self):
        """Test check endpoint without code parameter"""
        url = "/api/public/gift-cards/check/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "code is required")
