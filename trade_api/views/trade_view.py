from django.core.exceptions import ValidationError
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Action, Trade
from ..serializers import TradeSerializer
from ..services import TradeService


class TradeView(viewsets.GenericViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    @extend_schema(
        summary="List all trades",
        description="Returns a list of all the trades",
        responses=TradeSerializer(many=True),
        examples=[
            OpenApiExample(
                "Success",
                value=[
                    {
                        "id": "c3cfc74d-99dd-47cb-b39c-e8fc9f2dd36c",
                        "trading_entity": "Example entity",
                        "counterparty": "Example counterparty",
                        "direction": "buy",
                        "style": "forward",
                        "currency": "CAD",
                        "amount": "10000.00",
                        "underlying": ["CAD"],
                        "trade_date": None,
                        "value_date": None,
                        "delivery_date": None,
                        "strike": None,
                        "state": "needs reapproval",
                        "created_at": "2025-11-25T21:27:21.846508Z",
                        "updated_at": "2025-11-25T22:24:18.760284Z",
                    },
                    {
                        "id": "fc2d178d-2810-4291-a63e-b5f04201f7d3",
                        "trading_entity": "Trading entity",
                        "counterparty": "Counterpart",
                        "direction": "sell",
                        "style": "forward",
                        "currency": "CAD",
                        "amount": "10000.00",
                        "underlying": ["CAD"],
                        "trade_date": "2025-11-25T20:55:15.113853Z",
                        "value_date": "2025-11-25T20:55:22.416596Z",
                        "delivery_date": "2025-11-25T21:18:31.189938Z",
                        "strike": "1.000000",
                        "state": "executed",
                        "created_at": "2025-11-25T20:53:36.615607Z",
                        "updated_at": "2025-11-25T21:18:31.190228Z",
                    },
                ],
            ),
        ],
    )
    def list(self, request):
        trades = Trade.objects.all().order_by("-created_at")
        return Response(TradeSerializer(trades, many=True).data)

    @extend_schema(
        summary="Create trade",
        description="Creates a new trade as a draft.",
        request=TradeSerializer,
        responses={201: TradeSerializer},
        examples=[
            OpenApiExample(
                "Full request",
                request_only=True,
                value={
                    "trading_entity": "Trading entity",
                    "counterparty": "Counterpart",
                    "style": "style",
                    "direction": "sell",
                    "currency": "CAD",
                    "amount": 10000,
                    "underlying": ["USD"],
                },
            ),
            OpenApiExample(
                "Success",
                response_only=True,
                value={
                    "id": "a0aa98ff-89e9-46d7-9917-06df2f2abbe9",
                    "trading_entity": "Trading entity",
                    "counterparty": "Counterpart",
                    "direction": "sell",
                    "style": "forward",
                    "currency": "CAD",
                    "amount": "10000.00",
                    "underlying": ["CAD"],
                    "trade_date": None,
                    "value_date": None,
                    "delivery_date": None,
                    "strike": None,
                    "state": "draft",
                    "created_at": "2025-11-26T08:41:36.656036Z",
                    "updated_at": "2025-11-26T08:41:36.656059Z",
                },
            ),
        ],
    )
    def create(self, request):
        new_trade = TradeSerializer(data=request.data)
        if new_trade.is_valid():
            trade = new_trade.save()
            return Response(TradeSerializer(trade).data, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Invalid Trade", "details": new_trade.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Change trade",
        description="Change certain attributes of the trade",
        request=TradeSerializer,
        responses={200: TradeSerializer},
        examples=[
            OpenApiExample(
                "Request update",
                request_only=True,
                value={
                    "user_id": "26920541-6415-4ce3-85bb-167ea52e4b49",
                    "action": "update",
                    "fields": {"amount": 0},
                },
            ),
            OpenApiExample(
                "Request submit",
                request_only=True,
                value={
                    "user_id": "26920541-6415-4ce3-85bb-167ea52e4b49",
                    "action": "submit",
                },
            ),
            OpenApiExample(
                "Success",
                response_only=True,
                value={
                    "id": "2728e5b5-8830-4a94-8f3d-4fde9e1aa6ae",
                    "trading_entity": "Trading entity",
                    "counterparty": "Counterpart",
                    "direction": "sell",
                    "style": "forward",
                    "currency": "CAD",
                    "amount": "10000.00",
                    "underlying": ["CAD"],
                    "trade_date": None,
                    "value_date": None,
                    "delivery_date": None,
                    "strike": None,
                    "state": "needs reapproval",
                    "created_at": "2025-11-25T21:27:21.846508Z",
                    "updated_at": "2025-11-26T08:48:41.903746Z",
                },
            ),
        ],
    )
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

        if action is None:
            return Response(
                {"error": "No 'action' provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action not in Action._value2member_map_:
            all_value = [a.value for a in Action]
            return Response(
                {"error": f"'action' should be one of these options: {all_value}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fields = request.data.get("fields")

        if action == Action.UPDATE and fields is None:
            return Response(
                {"error": "No 'fields' provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == Action.BOOK and (fields is None or "strike" not in fields):
            return Response(
                {
                    "error": f"'strike' must be precised in 'fields' for the action '{Action.BOOK}'",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            trade = TradeService.update(trade, action, user_id, updated_fields=fields)
        except ValidationError as error:
            return Response(
                {
                    "error": "Bad request",
                    "details": error,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(TradeSerializer(trade).data)
