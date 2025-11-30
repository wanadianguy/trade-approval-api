import csv
import io

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

    @staticmethod
    def export_trade_logs_to_csv(trade_id):
        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            raise NotFoundException({"error": "Trade not found"})

        trade_logs = trade.log.all().order_by("-timestamp")
        csv_logs = io.StringIO()

        if not trade_logs:
            return csv_logs

        columns = [
            "trading_entity",
            "counterparty",
            "direction",
            "style",
            "currency",
            "amount",
            "underlying",
            "trade_date",
            "value_date",
            "delivery_date",
            "strike",
            "state",
        ]

        writer = csv.DictWriter(csv_logs, fieldnames=columns)
        writer.writeheader()

        for log in trade_logs:
            row = {}
            for key in columns:
                row[f"{key}"] = log.new_state.get(key, "")
            writer.writerow(row)

        # Adds the first state before any changes
        row = {}
        for key in columns:
            row[f"{key}"] = trade_logs[len(trade_logs) - 1].previous_state.get(key, "")
        writer.writerow(row)

        csv_logs.seek(0)
        return csv_logs
