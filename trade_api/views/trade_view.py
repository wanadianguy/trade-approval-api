from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Trade
from ..serializers import TradeSerializer
from ..services import TradeService


class TradeView(viewsets.GenericViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer

    @extend_schema(
        summary="List trades (can filter by state)",
        description="Returns a list of all the trades paginated and potentially filtered by state",
        responses=TradeSerializer(many=True),
        examples=[
            OpenApiExample(
                "Success",
                value={
                    "page": 1,
                    "total_pages": 1,
                    "trades": [
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
                },
            ),
        ],
    )
    def list(self, request):
        page = request.GET.get("page")
        if page is None:
            page = 1

        state = request.GET.get("state")

        page, total_pages, trades = TradeService.get_all_ordered_by_created_at(
            page=page, state=state
        )
        return Response(
            {
                "page": page,
                "total_pages": total_pages,
                "trades": TradeSerializer(trades, many=True).data,
            }
        )

    @extend_schema(
        summary="Get trade by id",
        description="Returns a list of all the trades",
        responses=TradeSerializer(many=True),
        examples=[
            OpenApiExample(
                "Success",
                value={
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
            ),
        ],
    )
    def get(self, request, id):
        trade = TradeService.get_by_id(id)
        return Response(TradeSerializer(trade).data)

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
        trade = TradeSerializer(data=request.data)
        if not trade.is_valid():
            return Response(
                {"error": "Invalid Trade", "details": trade.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trade = TradeService.create_trade(trade)
        return Response(TradeSerializer(trade).data, status=status.HTTP_201_CREATED)

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
        url_path=r"(?P<id>[0-9a-fA-F-]{36})",
    )
    def modify(self, request, id=None):
        action = request.data.get("action")
        fields = request.data.get("fields")
        user_id = request.data.get("user_id")
        trade = TradeService.update_trade(id, action, user_id, fields)

        return Response(TradeSerializer(trade).data)

    @extend_schema(
        summary="List diiferences between trades",
        description="Returns a the differences between 2 trades",
        examples=[
            OpenApiExample(
                "Request diff",
                request_only=True,
                value={
                    "trade1": {
                        "id": "756e561a-0d43-4c94-b0bb-7283bfd49eab",
                        "state": "draft",
                        "style": "style",
                        "amount": "10000.00",
                        "currency": "CAD",
                        "direction": "sell",
                        "created_at": "2025-11-26 12:04:33.574273+00:00",
                        "trade_date": "None",
                        "underlying": ["USD", "CAD"],
                        "updated_at": "2025-11-26 12:04:33.574314+00:00",
                        "value_date": "None",
                        "counterparty": "Counterpart",
                        "delivery_date": "None",
                        "trading_entity": "Trading entity",
                    },
                    "trade2": {
                        "id": "756e561a-0d43-4c94-b0bb-7283bfd49eab",
                        "state": "draft",
                        "style": "style",
                        "amount": "10000.00",
                        "currency": "CAD",
                        "direction": "sell",
                        "created_at": "2025-11-26 12:04:33.574273+00:00",
                        "trade_date": "None",
                        "underlying": ["CAD"],
                        "updated_at": "2025-11-26 12:04:57.661321+00:00",
                        "value_date": "None",
                        "counterparty": "Counterpart",
                        "delivery_date": "None",
                        "trading_entity": "Trading entity",
                    },
                },
            ),
            OpenApiExample(
                "Success",
                response_only=True,
                value={"underlying": {"previous": "['USD', 'CAD']", "new": "['CAD']"}},
            ),
        ],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path=r"diff",
    )
    def highlight_changes(self, request):
        trade1 = request.data.get("trade1")
        trade1 = TradeSerializer(data=trade1)
        trade2 = request.data.get("trade2")
        trade2 = TradeSerializer(data=trade2)
        if not trade1.is_valid():
            return Response(
                {"error": "Invalid Trade 'trade1'", "details": trade1.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not trade2.is_valid():
            return Response(
                {"error": "Invalid Trade 'trade2'", "details": trade2.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        diff = TradeService.get_diff_between_trades(trade1, trade2)
        return Response(diff)
