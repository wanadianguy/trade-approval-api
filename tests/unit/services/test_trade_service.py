from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from trade_api.models.trade import Trade, TradeDirection, TradeState

User = get_user_model()


class TradeServiceTests(TestCase):
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

    def test_update(self):
        return True
