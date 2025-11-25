import uuid

from django.db import models

from .trade import Trade, TradeState


class Action(models.TextChoices):
    SUBMIT = "submit"
    APPROVE = "approve"
    CANCEL = "cancel"
    UPDATE = "update"
    SEND = "send"
    BOOK = "book"


class TradeLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trade = models.ForeignKey(Trade, on_delete=models.CASCADE, related_name="log")
    user_id = models.UUIDField(editable=False)
    action = models.CharField(max_length=50, editable=False)
    state_before = models.CharField(
        max_length=50, choices=TradeState.choices, editable=False
    )
    state_after = models.CharField(
        max_length=50, choices=TradeState.choices, editable=False
    )
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    diff = models.JSONField(default=dict, editable=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Trade {self.trade.id} {self.action} at {self.timestamp.isoformat()}"
