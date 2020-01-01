import pandas as pd
from trading_calendars import get_calendar
from datetime import datetime
from multiprocessing import Pool

from data_management.contracts_db import ContractsDB
from data_management.quotes_db import QuotesDB



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
        self.contracts_db = ContractsDB()
        self.quotes_db = QuotesDB()


    def get_trading_calendar(self, exchange):
        """
        Get all trading days of an exchange and store into parameter as
        pandas series with index and data as datetime objects
        
        Parameters:
            exchanges: '[FWB', 'LSE']

        Returns
            Nothing
        """

        exchange_codes = {
            'FWB': 'XFRA',
            'IBIS': 'XFRA',
            'LSE': 'XLON',
            'LSEETF': 'XLON',
        }

        trading_calendar = get_calendar(exchange_codes[exchange])
        trading_days = trading_calendar.schedule.index.to_series(keep_tz=True)

        self.trading_days[exchange] = trading_days


    def get_missing_bars_count(self, df, exchange):
        # Get exchange data, if not yet present
        if exchange not in self.trading_days:
            self.get_trading_calendar(exchange)

        # Prepare data for comparison
        contract_trading_days = df.index.to_list()
        exchange_trading_days = self.trading_days[exchange]
        end_date = datetime.today().strftime('%Y-%m-%d')
        sliced_exchange_trading_days = exchange_trading_days[
            contract_trading_days[0]:end_date]
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


    def invalid_candles(self, ):
        """
        Invalid ccandles
        """

        # if max(candle.Open, candle.Low, candle.Close) > candle.High or min(
        # candle.Open, candle.High, candle.Close) < candle.Low:
        #     result['invalid_candle'].append(True)
        # else:
        #     result['invalid_candle'].append(False)

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
        #     if candle.Close == candle.Open:
        #         result['no_movement'].append(True)
        #     else:
        #         result['no_movement'].append(False)
        pass


    def check_single_quote(self, contract_id, exchange):
        result_dict = {}
        quotes = self.quotes_db.get_quotes(contract_id)
        
        df = pd.DataFrame()
        for quote in quotes:
            quote_dict = {}
            quote_dict['date'] = quote['date']
            quote_dict['open'] = quote['open']
            quote_dict['high'] = quote['high']
            quote_dict['low'] = quote['low']
            quote_dict['close'] = quote['close']
            quote_dict['volume'] = quote['volume']
            df = df.append(quote_dict, ignore_index=True)
        df = df.set_index('date')
        df.sort_index()

        result_dict = self.get_missing_bars_count(df, exchange)
        return result_dict


    def check_quotes_data_quality(self, ):
        # Todo: Implement parameters for filtering of contacts to check
        # Todo: Ad optional data start parameter
        # Todo: return dates of missing data days
        # Todo: Optimize perfomance
        
        # get contract ids and exchanges
        query_result = self.contracts_db.get_contracts()

        # reformat query result data for parallel execution
        contracts = []
        for contract in query_result[:100]:
            contracts.append((contract['contract_id'], contract['exchange']))
        
        # call worker and provide contract id plus exchange pairwise
        with Pool() as p:
            results = p.starmap(self.check_single_quote, contracts)

        # reformat results to df
        df = pd.DataFrame()
        for result in results:
            df = df.append(result, ignore_index=True)
        
        print(df)