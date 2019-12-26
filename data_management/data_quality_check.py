import pandas as pd
from trading_calendars import get_calendar



class DataQualityCheck():
    """
    todo:
    - extract single functions into own funtions and put them before main function
    - return a dict per instrument, containing pass of fail info for each single test and an overall result
    - make the test customizalble via parameters
    - the upper function, calling this function for each instrument, will create a dataframe
    from the returned dicts. The dataframe can then be inspected with the screener. If result is
    correct, it will be applied to the databases (alter pricedata or remove instrument)
    """


    def __init__(self):
        """

        """

        self.trading_days = {}


    def get_trading_days(self, exchange):
        """
        Get all trading days of an exchange and store into parameter as
        pandas series with index and data as datetime objects
        
        Parameters:
            exchange: 'FWB'

        Returns
            Nothing
        """

        exchange_names = {
            'FWB': 'XFRA',
        }

        trading_calendar = get_calendar(exchange_names[exchange])
        trading_days = trading_calendar.schedule.index.to_series(keep_tz=True)

        self.trading_days[exchange] = trading_days


    def get_missing_bars_count(self, df, exchange):
        # Get exchange data, if not yet present
        if exchange not in self.trading_days:
            self.get_trading_days(exchange)

        # Prepare data for comparison
        contract_trading_days = df.index.to_list()
        exchange_trading_days = self.trading_days[exchange]
        sliced_exchange_trading_days = exchange_trading_days[
            contract_trading_days[0]:contract_trading_days[-1]]
        sliced_exchange_trading_days = \
            sliced_exchange_trading_days.index.strftime('%Y-%m-%d').to_list()

        # Missing bars overall
        missing_bars_overall = 0
        for day in sliced_exchange_trading_days:
            if day not in contract_trading_days:
                missing_bars_overall += 1

        # Missing bars at end
        pos = sliced_exchange_trading_days.index(contract_trading_days[-1])
        missing_bars_at_end = len(sliced_exchange_trading_days) - (pos+1)

        result = {
            'missing_bars_overall': missing_bars_overall,
            'missing_bars_at_end': missing_bars_at_end
        }
        
        return result


    def missing_bars(self, ):
        """
        Missing bars overall
        """
        pass


    def invalid_candles(self, ):
        """
        Invalid ccandles
        """
        pass


    def value_jump(self, ):
        """
        Values jump
        """
        pass


    def no_movement(self, ):
        """
        No movement
        """
        pass


    def main(
        self, 
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