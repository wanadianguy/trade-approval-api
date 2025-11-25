import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from trade_api.models import Action, Trade, TradeDirection, TradeLog, TradeState

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
        TradeLog.objects.create(
            trade=self.trade,
            user_id=uuid.uuid4(),
            action=Action.SUBMIT,
            state_before=TradeState.DRAFT,
            state_after=TradeState.PENDING_APPROVAL,
        )

    def test_get_success(self):
        url = reverse("trade-log-by-trade", kwargs={"trade_id": self.trade.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(any(trade_log["action"] == Action.SUBMIT for trade_log in data))
