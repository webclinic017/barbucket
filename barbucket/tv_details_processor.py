import logging
from pathlib import Path
from os import path, listdir
from typing import Any, List, Dict

import pandas as pd

from .mediator import Mediator
from .custom_exceptions import QueryReturnedMultipleResultsError
from .custom_exceptions import QueryReturnedNoResultError
from .encoder import Encoder


logger = logging.getLogger(__name__)


class TvDetailsProcessor():
    """Processing of contract details provided by Tradingview screener"""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__file_row = None

    def read_tv_data(self) -> int:
        """Read contract details from tv files and write to database"""

        files = self.__get_files_from_dir()
        for file in files:
            file_data = self.__get_contracts_from_file(file=file)
            for row in file_data:
                self.__file_row = row
                try:
                    contract_id = self.__get_contract_id_from_db()
                except QueryReturnedNoResultError:
                    print("QueryReturnedNoResultError")  # Todo
                except QueryReturnedMultipleResultsError:
                    print("QueryReturnedMultipleResultsError")  # Todo
                else:
                    self.__write_contract_details_to_db(contract_id)
        return len(files)

    def __get_files_from_dir(self) -> List[Path]:
        """Create list of paths to all *.csv files in directory"""

        logger.debug(
            "Creating list of paths to all *.csv files in tv-directory.")
        dir_path = Path.home() / ".barbucket/tv_screener"  # Todo: Config
        tv_files = [path.join(dir_path, f) for f in listdir(
            dir_path) if f.endswith(".csv")]  # This also excludes directories
        return tv_files

    def __get_contracts_from_file(self, file: Path) -> List[Dict[str, Any]]:
        """Create formatted list of all contracts of a tv file"""

        logger.debug(f"Reading data from TV file {file}.")
        df = pd.read_csv(file, sep=",")
        file_contracts = []

        # Iterate over file rows
        for _, row in df.iterrows():
            row_formated = {}

            # Prepare the data
            row_formated['ticker'] = row['Ticker']
            row_formated['exchange'] = row['Exchange']
            row_formated['market_cap'] = int(row['Market Capitalization'])
            avg_vol_30_in_curr = row["Average Volume (30 day)"] * \
                row["Simple Moving Average (30)"]
            if pd.isna(avg_vol_30_in_curr):
                row_formated['avg_vol_30_in_curr'] = 0
            else:
                row_formated['avg_vol_30_in_curr'] = int(avg_vol_30_in_curr)
            row_formated['country'] = row['Country']
            if pd.isna(row["Number of Employees"]):
                row_formated['employees'] = 0
            else:
                row_formated['employees'] = int(row["Number of Employees"])
            if pd.isna(row["Gross Profit (FY)"]):
                row_formated['profit'] = 0
            else:
                row_formated['profit'] = int(row["Gross Profit (FY)"])
            if pd.isna(row["Total Revenue (FY)"]):
                row_formated['revenue'] = 0
            else:
                row_formated['revenue'] = int(row["Total Revenue (FY)"])
            file_contracts.append(row_formated)
        return file_contracts

    def __get_contract_id_from_db(self) -> int:
        """Get contract id from db matching some contract info"""

        logger.debug(f"Get contract id from db matching some contract info "
                     "from a tv file row.")
        ticker = self.__file_row['ticker'].replace(
            ".", " ")  # Todo: Create tool
        exchange = Encoder.decode_exchange_tv(self.__file_row['exchange'])
        filters = {
            'exchange': exchange,
            'contract_type_from_listing': "STOCK",
            'exchange_symbol': ticker}
        columns = ['contract_id']
        parameters = {'filters': filters, 'return_columns': columns}
        query_result = self.mediator.notify("get_contracts", parameters)
        if len(query_result) == 0:
            logger.warning(
                f"{len(query_result)} contracts found in master listing for "
                f"'{self.__file_row['ticker']}' on '"
                f"{self.__file_row['exchange']}'.")
            raise QueryReturnedNoResultError
        elif len(query_result) > 1:
            logger.warning(
                f"{len(query_result)} contracts found in master listing for '"
                f"{self.__file_row['ticker']}' on '"
                f"{self.__file_row['exchange']}'.")
            raise QueryReturnedMultipleResultsError
        else:
            return query_result[0]

    def __write_contract_details_to_db(self, contract_id: int) -> None:
        """Writing tv details to db"""

        market_cap = self.__file_row['market_cap'],
        avg_vol_30_in_curr = self.__file_row['avg_vol_30_in_curr'],
        country = self.__file_row['country'],
        employees = self.__file_row['employees'],
        profit = self.__file_row['profit'],
        revenue = self.__file_row['revenue']

        self.mediator.notify(
            "insert_tv_details", {
                'contract_id': contract_id,
                'market_cap': market_cap,
                'avg_vol_30_in_curr': avg_vol_30_in_curr,
                'country': country,
                'employees': employees,
                'profit': profit,
                'revenue': revenue})
