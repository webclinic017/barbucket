import logging
from datetime import date
from math import ceil

import numpy as np
import enlighten
from ib_insync.wrapper import RequestError

from barbucket.domain_model.data_classes import Contract
from barbucket.persistence.data_managers import \
    UniverseMembershipsDbManager, QuotesDbManager
from barbucket.api.tws_connector import TwsConnector
from barbucket.util.signal_handler import SignalHandler
from barbucket.util.config_reader import ConfigReader


_logger = logging.getLogger(__name__)


class QuotesProcessor():
    """Provides methods to download historical quotes from TWS."""

    def __init__(
            self,
            universe_db_manager: UniverseMembershipsDbManager,
            quotes_db_manager: QuotesDbManager,
            tws_connector: TwsConnector,
            # status_hadler: QuotesStatusHandler,
            signal_handler: SignalHandler,
            config_reader: ConfigReader) -> None:
        self._universes_db_manager = universe_db_manager
        self._quotes_db_manager = quotes_db_manager
        self._tws_connector = tws_connector
        # self._status_handler = status_hadler
        self._signal_handler = signal_handler
        self._config_reader = config_reader

    def download_historical_quotes(self, universe: str) -> None:
        """Download historical quotes from TWS

        :param universe: Universe to download quotes for
        :type universe: str
        """

        manager = enlighten.get_manager()  # Setup progress bar
        progress_bar = manager.counter(
            total=0, desc="Contracts", unit="contracts")
        contracts = self._universes_db_manager.get_members(universe=universe)
        progress_bar.total = len(contracts)
        self._tws_connector.connect()  # todo catch exceptioin if tws is not available
        for contract in contracts:
            if self._signal_handler.is_exit_requested():
                self._tws_connector.disconnect()
                return
            if self._is_quotes_recent(contract=contract):
                # log
                progress_bar.total -= 1
                progress_bar.update(incr=0)
                continue
            duration = self._get_download_duration(contract=contract)
            try:
                quotes = self._tws_connector.download_historical_quotes(
                    contract=contract, duration=duration)
            except RequestError as e:
                _logger.info(f"Problem downloading quotes for contract "
                             f"'{contract}': {e.message}")
                if e.reqId != -1:  # -1 are system errors
                    progress_bar.update(incr=1)
                continue
            else:
                self._quotes_db_manager.write_to_db(quotes=quotes)
                progress_bar.update(incr=1)
        _logger.info(
            f"Finished downloading historical data for universe "
            f"'{universe}'")
        self._tws_connector.disconnect()

    def _is_quotes_recent(self, contract: Contract) -> bool:
        redownload_days = self._config_reader.get_config_value_single(
            section='quotes', option='redownload_days')
        last_quote_date = self._quotes_db_manager.get_latest_quote_date(
            contract=contract)
        missing_quotes = np.busday_count(
            begindates=last_quote_date, enddates=date.today())
        return (missing_quotes < redownload_days)

    def _get_download_duration(self, contract: Contract) -> str:
        if self._quotes_db_manager.contract_has_quotes(contract=contract):
            initial_duration = self._config_reader.get_config_value_single(
                section="quotes", option="initial_duration")
            return initial_duration
        else:
            overlap_days = int(self._config_reader.get_config_value_single(
                section="quotes", option="overlap_days"))
            last_quote_date = self._quotes_db_manager.get_latest_quote_date(
                contract=contract)
            missing_quotes = np.busday_count(
                begindates=last_quote_date, enddates=date.today())
            # todo: this logic belongs into the API class
            if missing_quotes < 250:  # Api accepts only certain number of days
                duration = str(missing_quotes + overlap_days) + " D"
            else:
                duration = str(ceil(missing_quotes / 220)) + " Y"
            return duration
