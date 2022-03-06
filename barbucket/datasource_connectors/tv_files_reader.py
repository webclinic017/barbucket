from typing import List
from pathlib import Path
from os import listdir
from logging import getLogger

import pandas as pd

from barbucket.domain_model.tv_screener_row import TvScreenerRow
from barbucket.domain_model.types import Api, ApiNotationTranslator


_logger = getLogger(__name__)


class TvFilesReader():
    """ """
    _screener_rows: List[TvScreenerRow] = []
    _files_path: Path

    def __init__(self, files_path: Path) -> None:
        TvFilesReader._files_path = files_path

    @classmethod
    def get_all_rows(cls) -> List[TvScreenerRow]:
        files = cls._get_files(filespath=cls._files_path)
        for file in files:
            tsr = cls._get_tsr(file)
            cls._screener_rows += tsr
        return cls._screener_rows

    @classmethod
    def _get_files(cls, filespath: Path) -> List[Path]:
        # This also excludes sub-directories
        files = [file for file in filespath.iterdir()
                 if str(file).endswith(".csv")]
        return files

    @classmethod
    def _get_tsr(cls, file: Path) -> List[TvScreenerRow]:
        tsr = []
        rows = pd.read_csv(file, sep=",")
        for _, row in rows.iterrows():
            tsr.append(cls._create_tsr(row=row))
        return tsr

    @classmethod
    def _create_tsr(cls, row: pd.Series) -> TvScreenerRow:
        ticker_symbol = ApiNotationTranslator.get_ticker_symbol_from_api_notation(
            name=row['Ticker'],
            api=Api.TV)
        exchange = ApiNotationTranslator.get_exchange_from_api_notation(
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
