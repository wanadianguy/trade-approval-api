def trade_diff(trade_1, trade_2):
    diff = {}
    for field in trade_1:
        if trade_1[field] != trade_2[field]:
            diff[field] = {"previous": str(trade_1[field]), "new": str(trade_2[field])}
    return diff
