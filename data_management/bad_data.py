import pandas as pd

"""
todo:
- extract single functions into own funtions and put them before main function
- return a dict per instrument, containing pass of fail info for each single test and an overall result
- make the test customizalble via parameters
- the upper function, calling this function for each instrument, will create a dataframe
from the returned dicts. The dataframe can then be inspected with the screener. If result is
correct, it will be applied to the databases (alter pricedata or remove instrument)
"""


def get_trading_days(start, end):
    """
    
    
    Parameters:
    start: 'YYYY-MM-DD'
    end: 'YYYY-MM-DD'

    todo:
    - create external function, to scan through all data from an exchange, 
    and see on which day none of the instruments was traded. Those are non trading days.
    - store the found non-trading days in a databse/file, differentiate by exchange.
    """

    quotes = pd.read_csv('data\\^GDAXI.csv')
    quotes = quotes.set_index('Date')
    quotes = quotes[start:end]

    return len(quotes.index)

    # Missing bars overall
    result['missing_bars'] = index_trading_days - len(df)


    # Missing bars at begin
    # result.missing_bars_at_begin = df.index[0] - index_trading_days[0]

    # Missing bars at end
    # result.missing_bars_at_end = index_trading_days[-1] - df.index[-1]


def bad_data (
    df,
    index_trading_days,
    max_missing_bars = 0,
    # max_missing_bars_at_end = 0,
    # max_missing_bars_at_begin = 0,
    max_invalid_candle = 0,
    max_value_jump = 25,
    max_no_movement = 5):
    """
    df: 
    index_trading_days: int
    max_missing_bars = 0:
    max_missing_bars_at_end = 0:
    max_missing_bars_at_begin = 0:
    max_invalid_candle = 0:
    max_value_jump = 25:
    max_no_movement = 5:
    """

    result = {
        'flag': False,
        'missing_bars': 0,
        # 'missing_bars_at_begin': 0,
        # 'missing_bars_at_end': 0,
        'invalid_candle': [],
        'value_jump': [],
        'no_movement': []
    }


# New code below #################

def missing_bars():
    """
    Missing bars overall
    """
    pass

def missibng_bars_at_begin():
    """
    Missing bars at begin
    """
    pass

def missing_bars_at_end():
    """
    Missing bars at end
    """
    pass

def invalid_candles():
    """
    Invalid ccandles
    """
    pass

def value_jump():
    """
    Values jump
    """
    pass

def no_movement():
    """
    No movement
    """
    pass


# Old code below ##################

    for index, candle in df.iterrows():

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
        result['invalid_candle'].count(True) > max_invalid_candle or
        result['value_jump'].count(True) > max_value_jump or
        result['no_movement'].count(True) > max_no_movement
    ):
        result['flag'] = False
    else:
        result['flag'] = True


    return result