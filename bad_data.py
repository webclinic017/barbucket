def bad_data (
    df, 
    index_trading_days, 
    max_missing_bars = 0, 
    # max_missing_bars_at_end = 0, 
    # max_missing_bars_at_begin = 0, 
    max_invalid_candle = 0,
    max_value_jump = 25,
    max_no_movement = 5
):


    result = {
        'flag': False,
        'missing_bars': 0,
        # 'missing_bars_at_begin': 0,
        # 'missing_bars_at_end': 0,
        'invalid_candle': [],
        'value_jump': [],
        'no_movement': []
    }


    # Missing bars overall
    result.missing_bars = index_trading_days - len(
        df[index_trading_days[0]:index_trading_days[-1]])


    # # Missing bars at begin
    # result.missing_bars_at_begin = df.index[0] - index_trading_days[0]

    # # Missing bars at end
    # result.missing_bars_at_end = index_trading_days[-1] - df.index[-1]


    for candle in df:

        # Invalid candle
        if max(candle.Open, candle.Low, candle.Close) > candle.High or min(
        candle.Open, candle.High, candle.Close) < candle.Low:
            result['invalid_candle'].append(True)
        else:
            result['invalid_candle'].append(False)

        # Value jumps
        # FIXME
        result['value_jump'].append(False)

        # No movement from this open to this close
        if candle.Close == candle.Open:
            result['no_movement'].append(True)
        else:
            result['no_movement'].append(False)

    
    # Calculate result flag
    if (
        result['missing_bars'] > max_missing_bars or
        # result['missing_bars_at_begin'] > max_missing_bars_at_begin or
        # result['missing_bars_at_end'] > max_missing_bars_at_end or
        result['invalid_candle'] > max_invalid_candle or
        result['value_jump'] > max_value_jump or
        result['no_movement'] > max_no_movement
    ):
        result.flag = False
    else:
        result.flag = True


    return result