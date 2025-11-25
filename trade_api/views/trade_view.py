from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Action, Trade
from ..serializers import TradeSerializer
from ..services import TradeService


class TradeView(viewsets.GenericViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    # Returns all trades
    def list(self, request):
        trades = Trade.objects.all().order_by("-created_at")
        return Response(TradeSerializer(trades, many=True).data)

    # Handles trade creation
    def create(self, request):
        new_trade = TradeSerializer(data=request.data)
        if new_trade.is_valid():
            trade = new_trade.save()
            return Response(TradeSerializer(trade).data, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Invalid Trade", "details": new_trade.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handles action and data changes of a trade
    @action(
        detail=False,
        methods=["patch"],
        url_path=r"(?P<trade_id>[0-9a-fA-F-]{36})",
    )
    def modify(self, request, trade_id=None):
        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            return Response(
                {"error": "Trade not found"}, status=status.HTTP_404_NOT_FOUND
            )

        user_id = request.data.get("user_id")
        if (user_id) is None:
            return Response(
                {"error": "No 'user_id' provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        action = request.data.get("action")
        fields = request.data.get("fields")

        if fields is None:
            if action is None:
                return Response(
                    {"error": "'action' or 'fields' should be provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if action not in Action._value2member_map_:
                all_value = [a.value for a in Action]
                return Response(
                    {"error": f"'action' should be one of these options: {all_value}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                trade = TradeService.update(trade, action, user_id)
            except ValidationError as error:
                return Response(
                    {
                        "error": "Someting went wrong when trying to update the trade",
                        "details": error,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(TradeSerializer(trade).data)
        else:
            try:
                trade = TradeService.update(
                    trade, Action.UPDATE, user_id, updated_fields=fields
                )
            except ValidationError as error:
                return Response(
                    {
                        "error": "Someting went wrong when trying to update the trade",
                        "details": error,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(TradeSerializer(trade).data)
