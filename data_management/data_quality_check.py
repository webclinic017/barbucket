import numpy as np
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


    def check_too_few_quotes(self, df):
        # Check overall number of bars
        # Decide if contract should be kept
        # Return decision result

        MIN_QUOTES_COUNT = 250
        if len(df) < MIN_QUOTES_COUNT:
            return False
        else:
            return True


    def check_missing_bars_at_end(self, df):
        # Check for bars missing at end (to presence)
        # Decide if contract should be kept
        # Return decision result
        # Todo: Use trading calendar

        if len(df) == 0:
            return False
        
        MAX_MISSING_BARS_COUNT = 4
        start_date = str(df.index[-1].date())
        end_date = datetime.today().strftime('%Y-%m-%d')
        ndays = np.busday_count(start_date, end_date)
        if ndays > MAX_MISSING_BARS_COUNT:
            return False
        else:
            return True


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
        trading_days = trading_calendar.schedule.index
        trading_days = trading_days.to_series().dt.strftime('%Y-%m-%d')
        trading_days = pd.to_datetime(trading_days, format='%Y-%m-%d')
        self.trading_days[exchange] = trading_days


    def check_missing_bars(self, df, contract_id, exchange):
        # Download exchange trading calendar, if not yet present
        if exchange not in self.trading_days:
            self.get_trading_calendar(exchange)

        # Prepare data for comparison
        contract_trading_days = df.index.to_list()
        exchange_trading_days = self.trading_days[exchange]
        start_date = contract_trading_days[0]
        end_date = datetime.today().strftime('%Y-%m-%d')
        exchange_trading_days = exchange_trading_days[
            start_date:end_date]
        exchange_trading_days = \
            exchange_trading_days.index.strftime('%Y-%m-%d').to_list()

        # Find start of earliest gap
        MAX_GAP_SIZE = 4
        previous_missing_bars = 0
        remove_from = ''
        for day in exchange_trading_days:
            if day not in contract_trading_days:
                if previous_missing_bars >= MAX_GAP_SIZE:
                    remove_from = day
                previous_missing_bars += 1
            else:
                previous_missing_bars = 0

        # Return date, from where to delete quotes. -1 if none.
        if remove_from != '':
            return remove_from
        else:
            return -1



    def handle_single_contract(self, contract_id):
        # Get information for the contract
        contract = self.contracts_db.get_contracts(contract_id=contract_id)[0]
        
        # Get all quotes for the contract
        df = self.quotes_db.get_quotes(contract_id)

        # Delete contract, if too few quotes overall
        if not self.check_too_few_quotes(df):
            print(str(contract_id) + ' deleted, as too few quotes.')
            # self.contracts_db.delete_contract_id(contract_id)
            return

        # Delete contract, if too many quotes missing at end
        if not self.check_missing_bars_at_end(df):
            print(str(contract_id) + ' deleted, as too many quotes missing at end.')
            # self.contracts_db.delete_contract_id(contract_id)
            return

        # Handle missing bars
        del_from = self.check_missing_bars(df, contract_id, contract['exchange'])
        if del_from != -1:
            print(f'deletin from {del_from}')
            # self.quotes_db.delete_quotes_before_date(
            #     contract_id=contract_id, date=del_from)

        # Again, beacuse of previous gap removal:
        # Get all quotes for the contract
        df = self.quotes_db.get_quotes(contract_id)

        # Delete contract, if too few quotes overall
        if not self.check_too_few_quotes(df):
            print(str(contract_id) + ' deleted, as too few quotes after bars removal.')
            # self.contracts_db.delete_contract_id(contract_id)
            return




# Placeholders
    def _placeholder_check_bad_status(self, ):
        # Check if contract status is "no contract could be found"
        # Return result
        pass
    
    
    def _placeholder_check_invalid_candles(self, ):
        """
        Invalid ccandles
        Todo: Check for too large candles (spikes) as well
        Todo: Correct if possible
        Todo: Decide if contract is to delete. Return decision result.
        """

        # if max(candle.Open, candle.Low, candle.Close) > candle.High or min(
        # candle.Open, candle.High, candle.Close) < candle.Low:
        #     result['invalid_candle'].append(True)
        # else:
        #     result['invalid_candle'].append(False)
        pass


    def _placeholder_check_value_jump(self, ):
        """
        Values jump
        """
        pass


    def _placeholder_check_no_movement(self, ):
        """
        No movement
        """
        #     if candle.Close == candle.Open:
        #         result['no_movement'].append(True)
        #     else:
        #         result['no_movement'].append(False)
        pass


    def _placeholder_remove_duplicate_contracts(self, ):
        # for contracts with identical name
            # keep the one with the most quotes / biggest volume
            # remove the other contracts
        # from here, use smart routing for all contracts
        pass




# Deprecated
    def _deprecated_remove_quoteless_contracts(self):
        # removes all contracts that have no quotes linked

        # conn = self.quotes_db.connect()
        # cur = conn.cursor()

        # query = """
        # DELETE FROM contracts
        # WHERE contract_id IN (
        #     SELECT
        #         contract_id
        #     FROM
        #         contracts c
        #     WHERE
        #         NOT EXISTS (
        #             SELECT 
        #                 1 
        #             FROM 
        #                 quotes
        #             WHERE 
        #                 contract_id = c.contract_id
        #         )
        # )
        # """
        # cur.execute(query)

        # conn.commit()
        # cur.close()
        # self.quotes_db.disconnect(conn)
        pass


    def _deprecated_check_quotes_data_quality_worker(self, contract_id, exchange):
        # result_dict = {}
     
        # # Get all quotes for the contract
        # quotes = self.quotes_db.get_quotes(contract_id)

        # # Abort contract if no quotes available
        # if len(quotes) == 0:
        #     print('-' + str(contract_id) + 'XXXXXXX' + '-')
        #     return

        # # Reformat quotes to df
        # # Todo: use pandas method for querying
        # quotes_dict = {}
        # i = 0
        # for quote in quotes:
        #     quotes_dict[i] = {
        #         'date': quote['date'],
        #         'open': quote['open'],
        #         'high': quote['high'],
        #         'low': quote['low'],
        #         'close': quote['close'],
        #         'volume': quote['volume']}
        #     i += 1
        # df = pd.DataFrame.from_dict(data=quotes_dict, orient='index')
        # df = df.set_index('date')
        # df.sort_index()

        # # Check for missing bars
        # self.handle_missing_bars(df, contract_id, exchange)
        # print('.')
        pass


    def _deprecated_check_quotes_data_quality(self, ):
        # # Todo: Implement parameters for filtering of contacts to check

        # # Delete contracts that have an error status
        # self.contracts_db.delete_bad_status_contracts()
        
        # # get all contract ids and exchanges
        # query_result = self.contracts_db.get_contracts()

        # # reformat query result data for parallel execution
        # contracts = []
        # for contract in query_result[:]:
        #     # todo: if contract status is ...
        #     contracts.append((contract['contract_id'], contract['exchange']))
        
        # # call worker and provide contract id plus exchange pairwise
        # with Pool() as p:
        #     p.starmap(self.check_quotes_data_quality_worker, contracts)

        # self.remove_quoteless_contracts()
        pass