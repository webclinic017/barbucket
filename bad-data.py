def bad_data (df, index_trading_days):

    result = {
        'missing_bars': 0,
        'missing_bars_at_begin': 0,
        'missing_bars_at_end': 0,
        'invalid_candle': [],
        'value_jump': [],
        'no_movement': []
    }

    # Missing bars overall
    result.missing_bars = len(index_trading_days) - len(df)

    # Missing bars at begin
    result.missing_bars_at_begin = df.index[0] - index_trading_days[0]

    # Missing bars at end
    result.missing_bars_at_end = index_trading_days[-1] - df.index[-1]


    for candle in df:

        # Invalid candle
        if max(candle.open, candle.low, candle.close) > candle.high or min(
        candle.open, candle.high, candle.close) < candle.low:
            result['invalid_candle'].append(True)
        else:
            result['invalid_candle'].append(False)

        # Value jumps
        # FIXME
        result['invalid_candle'].append(False)

        # No movement from this open to this close
        if candle.close == candle.open:
            result['no_movement'].append(True)
        else:
            result['no_movement'].append(False)

    return result