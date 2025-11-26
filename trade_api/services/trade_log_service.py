from ..exceptions import NotFoundException
from ..models import Trade


class TradeLogService:
    @staticmethod
    def get_all_by_trade_id_ordered_by_timestamp(trade_id):
        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            raise NotFoundException({"error": "Trade not found"})

        return trade.log.all().order_by("-timestamp")
