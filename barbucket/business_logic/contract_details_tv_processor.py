from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
import enlighten

from barbucket.datasource_connectors.tv_files_reader import TvFilesReader
from barbucket.persistence.data_managers import ContractDetailsTvDbManager, ContractsDbManager
from barbucket.domain_model.data_classes import ContractDetailsTv, Contract
from barbucket.domain_model.tv_screener_row import TvScreenerRow
from barbucket.domain_model.types import ContractType


class ContractDetailsTvProcessor():
    _files_reader: TvFilesReader
    _details_db_manager: ContractDetailsTvDbManager
    _contracts_db_manager: ContractsDbManager
    _session: Session

    def __init__(self,
                 files_reader: TvFilesReader,
                 details_db_manager: ContractDetailsTvDbManager,
                 contracts_db_manager: ContractsDbManager,
                 session: Session) -> None:
        ContractDetailsTvProcessor._files_reader = files_reader
        ContractDetailsTvProcessor._details_db_manager = details_db_manager
        ContractDetailsTvProcessor._contracts_db_manager = contracts_db_manager
        ContractDetailsTvProcessor._session = session

    @classmethod
    def update_ib_contract_details(cls) -> None:
        pb_manager = enlighten.get_manager()  # Setup progress bar
        progress_bar = pb_manager.counter(
            total=0, desc="Contracts", unit="contracts")
        sceener_rows = cls._files_reader.get_all_rows()
        progress_bar.total = len(sceener_rows)
        for row in sceener_rows:
            cls._handle_row(row=row)
            progress_bar.update(inc=1)
        cls._session.close()

    @classmethod
    def _handle_row(cls, row: TvScreenerRow) -> None:
        # Check if matching contract exists in db
        contract_filters = (
            Contract.exchange == row.exchange,
            Contract.contract_type == ContractType.STOCK.name,
            Contract.exchange_symbol == row.ticker_symbol)
        try:
            contract = cls._contracts_db_manager.get_one_by_filters(
                filters=contract_filters)
        except NoResultFound:
            pass  # log
        except MultipleResultsFound:
            pass  # log
        else:
            # Add screener data to db
            details = ContractDetailsTv(
                contract=contract,
                market_cap=row.market_cap,
                avg_vol_30_in_curr=row.avg_vol_30_in_curr,
                country=row.country,
                employees=row.employees,
                profit=row.profit,
                revenue=row.revenue)
            cls._details_db_manager.write_to_db(details=details)
            cls._session.commit()
