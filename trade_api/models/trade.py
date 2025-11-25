import uuid
from typing import List, cast

from django.core.exceptions import ValidationError
from django.db import models


class TradeState(models.TextChoices):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending approval"
    NEEDS_REAPPROVAL = "needs reapproval"
    APPROVED = "approved"
    SENT = "sent"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class TradeDirection(models.TextChoices):
    BUY = "buy"
    SELL = "sell"


def validate_three_char_list(value):
    if not isinstance(value, list):
        raise ValidationError("Value must be a list")
    for item in value:
        if not isinstance(item, str) or len(item) > 3:
            raise ValidationError(
                "Each item must be a string and at most 3 characters long"
            )


class Trade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trading_entity = models.CharField(max_length=300)
    counterparty = models.CharField(max_length=300)
    direction = models.CharField(max_length=4, choices=TradeDirection.choices)
    style = models.CharField(max_length=100, default="forward")
    currency = models.CharField(max_length=3)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    underlying = models.JSONField(default=list, validators=[validate_three_char_list])
    trade_date = models.DateTimeField(null=True, blank=True)
    value_date = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateTimeField(null=True, blank=True)
    strike = models.DecimalField(max_digits=30, decimal_places=6, null=True, blank=True)
    state = models.CharField(
        max_length=20, choices=TradeState.choices, default=TradeState.DRAFT
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        currency = cast(str, self.currency)
        currencies = cast(List[str], self.underlying or [])
        if currency not in currencies:
            currencies.append(currency)
            self.underlying = currencies
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trade {self.pk} ({self.state})"
