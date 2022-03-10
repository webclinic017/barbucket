from typing import List
from pathlib import Path
from logging import getLogger

import pandas as pd

from barbucket.domain_model.tv_screener_row import TvScreenerRow
from barbucket.domain_model.types import Api, ApiNotationTranslator


_logger = getLogger(__name__)


class TvFilesReader():
    """ """

    def __init__(self, files_path: Path,
                 api_notation_translator: ApiNotationTranslator) -> None:
        self._screener_rows: List[TvScreenerRow] = []
        self._files_path = files_path
        self._api_notation_translator = api_notation_translator

    def get_all_rows(self) -> List[TvScreenerRow]:
        files = self._get_files(filespath=self._files_path)
        for file in files:
            tsr = self._get_tsr(file)
            self._screener_rows += tsr
        return self._screener_rows

    def _get_files(self, filespath: Path) -> List[Path]:
        # This also excludes sub-directories
        files = [file for file in filespath.iterdir()
                 if str(file).endswith(".csv")]
        return files

    def _get_tsr(self, file: Path) -> List[TvScreenerRow]:
        tsr = []
        rows = pd.read_csv(file, sep=",")
        for _, row in rows.iterrows():
            tsr.append(self._create_tsr(row=row))
        return tsr

    def _create_tsr(self, row: pd.Series) -> TvScreenerRow:
        ticker_symbol = self._api_notation_translator.get_ticker_symbol_from_api_notation(
            name=row['Ticker'],
            api=Api.TV)
        exchange = self._api_notation_translator.get_exchange_from_api_notation(
            name=row['Exchange'],
            api=Api.TV)
        tsr = TvScreenerRow(
            ticker_symbol=ticker_symbol.name,
            exchange=exchange.name,
            market_cap=(int(row['Market Capitalization']) if not pd.isna(
                row["Number of Employees"]) else None),
            avg_vol_30_in_curr=(
                int(row["Average Volume (30 day)"] *
                    row["Simple Moving Average (30)"])
                if not (pd.isna(row["Average Volume (30 day)"])
                        or pd.isna(row["Simple Moving Average (30)"]))
                else None),
            country=row['Country'],
            employees=(int(row["Number of Employees"]) if not pd.isna(
                row["Number of Employees"]) else None),
            profit=(int(row["Gross Profit (FY)"]) if not pd.isna(
                row["Gross Profit (FY)"]) else None),
            revenue=(int(row["Total Revenue (FY)"]) if not pd.isna(
                row["Total Revenue (FY)"]) else None))
        return tsr
