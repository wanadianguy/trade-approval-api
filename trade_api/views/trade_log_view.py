from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import TradeLog
from ..serializers import TradeLogSerializer
from ..services import TradeLogService


class TradeLogView(viewsets.GenericViewSet):
    queryset = TradeLog.objects.all()
    serializer_class = TradeLogSerializer

    @extend_schema(
        summary="List logs of trade",
        description="Returns a list of all the logs of a trade",
        responses=TradeLogSerializer(many=True),
        examples=[
            OpenApiExample(
                "Success",
                value=[
                    {
                        "id": "d16513b6-bad8-4349-8576-4e52af57a82d",
                        "user_id": "fc2d178d-2810-4291-a63e-b5f04201f7d3",
                        "action": "approve",
                        "state_before": "pending approval",
                        "state_after": "approved",
                        "timestamp": "2025-11-25T20:55:15.120800Z",
                        "diff": {
                            "state": {
                                "new": "approved",
                                "previous": "pending approval",
                            },
                            "trade_date": {
                                "new": "2025-11-25 20:55:15.113853",
                                "previous": "None",
                            },
                        },
                        "trade": "fc2d178d-2810-4291-a63e-b5f04201f7d3",
                    },
                    {
                        "id": "5d9a3088-cebf-4403-b433-13226c09de74",
                        "user_id": "fc2d178d-2810-4291-a63e-b5f04201f7d3",
                        "action": "submit",
                        "state_before": "draft",
                        "state_after": "pending approval",
                        "timestamp": "2025-11-25T20:55:07.212071Z",
                        "diff": {
                            "state": {"new": "pending approval", "previous": "draft"}
                        },
                        "trade": "fc2d178d-2810-4291-a63e-b5f04201f7d3",
                    },
                ],
            ),
        ],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path=r"(?P<trade_id>[0-9a-fA-F-]{36})",
        url_name="by-trade",
    )
    def get(self, request, trade_id=None):
        logs = TradeLogService.get_all_by_trade_id_ordered_by_timestamp(trade_id)
        return Response(TradeLogSerializer(logs, many=True).data)
