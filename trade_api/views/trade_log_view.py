from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Trade
from ..serializers import TradeLogSerializer


class TradeLogView(viewsets.GenericViewSet):
    @action(detail=False, methods=["get"], url_path=r"(?P<trade_id>[0-9a-fA-F-]{36})")
    def get(self, request, trade_id=None):
        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            return Response(
                {"error": "Trade not found"}, status=status.HTTP_404_NOT_FOUND
            )

        logs = trade.log.all().order_by("-timestamp")
        return Response(TradeLogSerializer(logs, many=True).data)
