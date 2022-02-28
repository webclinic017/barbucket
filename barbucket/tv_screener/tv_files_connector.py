from typing import List
from pathlib import Path
from os import listdir
from logging import getLogger

import pandas as pd

from barbucket.tv_screener.tv_screener_row import TvScreenerRow
from barbucket.encodings import Api, Exchange, Symbol


_logger = getLogger(__name__)


class TvFilesReader():
    """ """
    _screener_rows: List[TvScreenerRow]
    _files_path: Path

    def __init__(self, files_path: Path) -> None:
        TvFilesReader._files_path = files_path

    @classmethod
    def get_all_rows(cls) -> List[TvScreenerRow]:
        files = cls._get_files(filespath=cls._files_path)
        for file in files:
            tsr = cls._get_tsr(file)
            cls._screener_rows.append(tsr)
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
        tsr = TvScreenerRow(
            ticker=Symbol.decode(
                name=row['Ticker'],
                from_api=Api.TV),
            exchange=Exchange.decode(
                name=row['Exchange'],
                from_api=Api.TV),
            market_cap=int(row['Market Capitalization']),
            avg_vol_30_in_curr=(
                int(row["Average Volume (30 day)"] *
                    row["Simple Moving Average (30)"])
                if (pd.isna(row["Average Volume (30 day)"])
                    or pd.isna(row["Simple Moving Average (30)"]))
                else 0),
            country=row['Country'],
            employees=(int(row["Number of Employees"]) if not pd.isna(
                row["Number of Employees"]) else 0),
            profit=(int(row["Gross Profit (FY)"]) if not pd.isna(
                row["Gross Profit (FY)"]) else 0),
            revenue=(int(row["Total Revenue (FY)"]) if not pd.isna(
                row["Total Revenue (FY)"]) else 0))
        return tsr
