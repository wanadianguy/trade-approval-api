from datetime import date


def trade_diff(trade_1, trade_2):
    diff = {}
    for field in trade_1:
        if isinstance(trade_1[field], date):
            continue
        if trade_1[field] != trade_2[field]:
            diff[field] = {"previous": str(trade_1[field]), "new": str(trade_2[field])}
    return diff
