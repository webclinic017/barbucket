import numpy as np
import pandas as pd
from trading_calendars import get_calendar
from datetime import datetime
from multiprocessing import Pool
import configparser

from barbucket.contracts_db import ContractsDB
from barbucket.quotes_db import QuotesDB



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

        self.__trading_days = {}
        self.__contracts_db = ContractsDB()
        self.__quotes_db = QuotesDB()

        self.__config = configparser.ConfigParser()
        self.__config.read('barbucket/config.ini')


    def __check_too_few_quotes(self, df):
        # Check overall number of bars
        # Decide if contract should be kept
        # Return decision result
        # Todo: Return barcount

        MIN_QUOTES_COUNT = self.__config.getint(
            'quality_check',
            'min_quotes_count')
        if len(df) < MIN_QUOTES_COUNT:
            return False
        else:
            return True


    def __check_missing_quotes_at_end(self, df):
        # Check for bars missing at end (to presence)
        # Decide if contract should be kept
        # Return decision result
        # Todo: Use trading calendar
        # Todo: Return missing bars count

        if len(df) == 0:
            return False
        
        MAX_MISSING_QUOTES_COUNT = self.__config.getint(
            'quality_check',
            'max_missing_quotes_at_end')

        start_date = str(df.index[-1].date())
        end_date = datetime.today().strftime('%Y-%m-%d')
        ndays = np.busday_count(start_date, end_date)
        if ndays > MAX_MISSING_QUOTES_COUNT:
            return False
        else:
            return True


    def __get_trading_calendar(self, exchange):
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
        self.__trading_days[exchange] = trading_days


    def __check_missing_bars(self, df, contract_id, exchange):
        # Todo: MAX_GAP_SIZE as parameter

        # Download exchange trading calendar, if not yet present
        if exchange not in self.__trading_days:
            self.__get_trading_calendar(exchange)

        # Prepare data for comparison
        contract_trading_days = df.index.strftime('%Y-%m-%d').to_list()
        exchange_trading_days = self.__trading_days[exchange]
        start_date = contract_trading_days[0]
        end_date = datetime.today().strftime('%Y-%m-%d')
        exchange_trading_days = exchange_trading_days[
            start_date:end_date]
        exchange_trading_days = \
            exchange_trading_days.index.strftime('%Y-%m-%d').to_list()

        # Find start of earliest gap
        MAX_GAP_SIZE = self.__config.getint('quality_check', 'max_gap_size')
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
        contract = self.__contracts_db.get_contracts(contract_id=contract_id)[0]
        
        # Get all quotes for the contract
        df = self.__quotes_db.get_quotes(contract_id)

        # Delete contract, if too few quotes overall
        if not self.__check_too_few_quotes(df):
            print(str(contract_id) + ' Deleted, as too few quotes. ', end='')
            self.__contracts_db.delete_contract_id(contract_id)
            return

        # Delete contract, if too many quotes missing at end
        if not self.check_missing_quotes_at_end(df):
            print(str(contract_id) + ' Deleted, as too many quotes missing at end. ', end='')
            self.contracts_db.delete_contract_id(contract_id)
            return

        # Handle missing bars
        del_from = self.__check_missing_bars(df, contract_id, contract['exchange'])
        if del_from != -1:
            print(f'Deleting from {del_from} ', end='')
            self.__quotes_db.delete_quotes_before_date(
                contract_id=contract_id, date=del_from)

        # Again, beacuse of previous gap removal:
        # Get all quotes for the contract
        df = self.__quotes_db.get_quotes(contract_id)

        # Delete contract, if too few quotes overall
        if not self.__check_too_few_quotes(df):
            print(str(contract_id) + ' Deleted, as too few quotes after bars removal. ', end='')
            self.__contracts_db.delete_contract_id(contract_id)
            return




# Placeholders
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