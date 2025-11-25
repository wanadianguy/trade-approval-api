from rest_framework import serializers

from ..models import Trade
from ..utils import compare_dates


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade
        fields = "__all__"
        read_only_fields = ["id", "strike", "state", "created_at", "updated_at"]

    def validate(self, attrs):
        trade_date = attrs.get("trade_date")
        value_date = attrs.get("value_date")
        delivery_date = attrs.get("delivery_date")
        if not (
            compare_dates(trade_date, value_date)
            and compare_dates(value_date, delivery_date)
            and compare_dates(trade_date, delivery_date)
        ):
            raise serializers.ValidationError(
                "Dates must satisfy: Trade Date ≤ Value Date ≤ Delivery Date."
            )
        return attrs
