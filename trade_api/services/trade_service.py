from django.core.paginator import Paginator
from django.utils import timezone

from ..exceptions import BadRequestException, NotFoundException
from ..models import Action, Trade, TradeLog, TradeState
from ..utils import trade_diff

# Table of valid actions depending on the trade state
valid_transitions = {
    TradeState.DRAFT: {
        Action.SUBMIT: TradeState.PENDING_APPROVAL,
        Action.UPDATE: TradeState.DRAFT,
    },
    TradeState.PENDING_APPROVAL: {
        Action.APPROVE: TradeState.APPROVED,
        Action.CANCEL: TradeState.CANCELLED,
        Action.UPDATE: TradeState.NEEDS_REAPPROVAL,
    },
    TradeState.NEEDS_REAPPROVAL: {
        Action.APPROVE: TradeState.APPROVED,
        Action.CANCEL: TradeState.CANCELLED,
        Action.UPDATE: TradeState.NEEDS_REAPPROVAL,
    },
    TradeState.APPROVED: {
        Action.SEND: TradeState.SENT,
        Action.CANCEL: TradeState.CANCELLED,
        Action.UPDATE: TradeState.NEEDS_REAPPROVAL,
    },
    TradeState.SENT: {
        Action.BOOK: TradeState.EXECUTED,
        Action.CANCEL: TradeState.CANCELLED,
    },
}


class TradeService:
    @staticmethod
    def get_all_ordered_by_created_at(page: int = 1, per_page: int = 10):
        trades = Trade.objects.order_by("-created_at")
        paginator = Paginator(trades, per_page)
        trade_page = paginator.get_page(page)
        return trade_page.number, paginator.num_pages, list(trade_page)

    @staticmethod
    def create_trade(trade):
        return trade.save()

    @staticmethod
    def update_trade(trade_id, action, user_id, updated_fields):
        try:
            trade = Trade.objects.get(id=trade_id)
        except Trade.DoesNotExist:
            raise NotFoundException({"error": "Trade not found"})

        if (user_id) is None:
            raise BadRequestException({"error": "No 'user_id' provided"})

        if action is None:
            raise BadRequestException({"error": "No 'action' provided"})

        if action not in Action._value2member_map_:
            all_value = [a.value for a in Action]
            raise BadRequestException(
                {"error": f"'action' should be one of these options: {all_value}"}
            )

        if action == Action.UPDATE and updated_fields is None:
            raise BadRequestException({"error": "No 'fields' provided"})

        if action == Action.BOOK and (
            updated_fields is None or "strike" not in updated_fields
        ):
            raise BadRequestException(
                {
                    "error": f"'strike' must be precised in 'fields' for the action '{Action.BOOK}'"
                }
            )

        # Checks if action is valid for the current trade's state with the table valid_transitions
        if action not in valid_transitions.get(trade.state, {}):
            raise BadRequestException(
                {"error": f"Invalid action '{action}' for state '{trade.state}'"}
            )

        # Takes a snapshot of the trade's current state
        current_trade = {
            field.name: str(getattr(trade, field.name)) for field in trade._meta.fields
        }

        if updated_fields:
            for field, value in updated_fields.items():
                if hasattr(trade, field):
                    if field == "strike" and action != Action.BOOK:
                        continue
                    setattr(trade, field, value)

        # Changes the trade's state
        trade.state = valid_transitions[trade.state][action]

        # Logs specific actions
        if action == Action.APPROVE:
            trade.trade_date = timezone.now()
        elif action == Action.SEND:
            trade.value_date = timezone.now()
        elif action == Action.BOOK:
            trade.delivery_date = timezone.now()
        elif action == Action.UPDATE:
            trade.trade_date = None
            trade.value_date = None
            trade.delivery_date = None

        trade.save()

        # Takes a snapshot of the trade's new state
        new_trade = {
            field.name: str(getattr(trade, field.name)) for field in trade._meta.fields
        }

        # Creates a table of differences bewteen the snapshots
        diff = trade_diff(current_trade, new_trade)

        TradeLog.objects.create(
            trade=trade,
            user_id=user_id,
            action=action,
            previous_state=current_trade,
            new_state=new_trade,
            diff=diff,
        )

        return trade

    @staticmethod
    def get_diff_between_trades(trade1, trade2):
        diff = trade_diff(trade1.validated_data, trade2.validated_data)
        return diff
