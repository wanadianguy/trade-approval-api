import uuid

from django.db import models

from .trade import Trade


class Action(models.TextChoices):
    SUBMIT = "submit"
    APPROVE = "approve"
    CANCEL = "cancel"
    UPDATE = "update"
    SEND = "send"
    BOOK = "book"


class TradeLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trade = models.ForeignKey(
        Trade, on_delete=models.CASCADE, related_name="log", editable=False
    )
    user_id = models.UUIDField(editable=False)
    action = models.CharField(max_length=10, choices=Action.choices, editable=False)
    previous_state = models.JSONField(default=dict, editable=False)
    new_state = models.JSONField(default=dict, editable=False)
    diff = models.JSONField(default=dict, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return f"Trade {self.trade} {self.action} at {self.timestamp.isoformat()}"
