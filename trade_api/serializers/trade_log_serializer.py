from rest_framework import serializers

from ..models import TradeLog


class TradeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TradeLog
        fields = "__all__"
        read_only_fields = [
            "trade",
            "user_id",
            "action",
            "state_before",
            "state_after",
            "timestamp",
            "diff",
        ]
