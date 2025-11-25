from django.core.exceptions import ValidationError

from ..models import Action, TradeLog, TradeState
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
        Action.UPDATE: TradeState.PENDING_APPROVAL,
    },
    TradeState.NEEDS_REAPPROVAL: {
        Action.APPROVE: TradeState.APPROVED,
        Action.CANCEL: TradeState.CANCELLED,
        Action.UPDATE: TradeState.NEEDS_REAPPROVAL,
    },
    TradeState.APPROVED: {
        Action.SEND: TradeState.SENT,
        Action.CANCEL: TradeState.CANCELLED,
    },
    TradeState.SENT: {
        Action.BOOK: TradeState.EXECUTED,
        Action.CANCEL: TradeState.CANCELLED,
    },
}


class TradeService:
    @staticmethod
    def update(trade, action, user_id, updated_fields=None):
        starting_state = trade.state

        if action not in valid_transitions.get(starting_state, {}):
            raise ValidationError(
                f"Invalid action '{action}' for state '{starting_state}'"
            )

        # Takes a snapshot of the trade's current state
        current_trade = {
            field.name: getattr(trade, field.name) for field in trade._meta.fields
        }

        if updated_fields:
            for field, value in updated_fields.items():
                if hasattr(trade, field):
                    print(field)
                    setattr(trade, field, value)

        # Change the trade's state
        trade.state = valid_transitions[starting_state][action]
        trade.save()

        # Takes a snapshot of the trade's new state
        new_trade = {
            field.name: getattr(trade, field.name) for field in trade._meta.fields
        }

        diff = trade_diff(current_trade, new_trade)

        TradeLog.objects.create(
            trade=trade,
            user_id=user_id,
            action=action,
            state_before=starting_state,
            state_after=trade.state,
            diff=diff,
        )

        return trade
