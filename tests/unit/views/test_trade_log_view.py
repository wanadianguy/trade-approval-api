import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from trade_api.models import Action, Trade, TradeDirection, TradeState

User = get_user_model()


class TradeViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="username", password="password")
        self.client.force_authenticate(user=self.user)
        self.trade = Trade.objects.create(
            trading_entity="test entity",
            counterparty="test Counterpart",
            direction=TradeDirection.SELL,
            currency="CAD",
            amount=2000,
        )

    def test_get_success(self):
        url = reverse("trade-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(any(trade["trading_entity"] == "test entity" for trade in data))

    def test_create_success(self):
        url = reverse("trade-list")
        response = self.client.post(
            url,
            data={
                "trading_entity": "test entity",
                "counterparty": "test Counterpart",
                "direction": TradeDirection.SELL,
                "currency": "CAD",
                "amount": 2000,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["trading_entity"] == "test entity")

    def test_create_invalid_field(self):
        url = reverse("trade-list")
        response = self.client.post(
            url,
            data={"invalid": "invalid"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_create_missing_field(self):
        url = reverse("trade-list")
        response = self.client.post(
            url,
            data={
                "trading_entity": "test entity",
                "counterparty": "test Counterpart",
                "direction": TradeDirection.SELL,
                "amount": 2000,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_modify_success_with_action(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(
            url,
            data={
                "user_id": self.user.id,
                "action": Action.SUBMIT,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["state"], TradeState.PENDING_APPROVAL)
        self.trade.refresh_from_db()
        self.assertEqual(self.trade.state, TradeState.PENDING_APPROVAL)

    def test_modify_success_with_fields(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(
            url,
            data={"user_id": self.user.id, "fields": {"currency": "USD"}},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["currency"], "USD")
        self.assertTrue(data["currency"] in data["underlying"])

    def test_modify_trade_not_found(self):
        url = reverse("trade-modify", kwargs={"trade_id": uuid.uuid4()})
        response = self.client.patch(url, data={"user_id": self.user.id}, format="json")
        self.assertEqual(response.status_code, 404)

    def test_modify_missing_user_id(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(url, data={}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_modify_invalid_action(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(
            url, data={"user_id": self.user.id, "action": "INVALID"}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_modify_invalid_action_for_state(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(
            url, data={"user_id": self.user.id, "action": Action.APPROVE}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_modify_missing_action_and_fields(self):
        url = reverse("trade-modify", kwargs={"trade_id": self.trade.id})
        response = self.client.patch(url, data={"user_id": self.user.id}, format="json")
        self.assertEqual(response.status_code, 400)
