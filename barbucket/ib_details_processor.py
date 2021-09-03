import logging
from typing import Any

import enlighten

from .mediator import Mediator
from .custom_exceptions import QueryReturnedNoResultError
from .custom_exceptions import QueryReturnedMultipleResultsError
from .base_component import BaseComponent


class IbDetailsProcessor(BaseComponent):
    """Docstring"""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__contracts = None
        self.__details = None
        self.__pbar = None

    def __setup_progress_bar(self) -> None:
        manager = enlighten.get_manager()
        self.__pbar = manager.counter(
            total=len(self.__contracts),
            desc="Contracts", unit="contracts")

    def __get_contracts(self) -> None:
        """Get contracts from db, where IB details are missing"""

        columns = ['contract_id', 'contract_type_from_listing',
                   'broker_symbol', 'exchange', 'currency']
        filters = {'primary_exchange': "NULL"}
        parameters = {'filters': filters, 'return_columns': columns}
        self.__contracts = self.mediator.notify("get_contracts", parameters)
        logging.info(f"Found {len(self.__contracts)} contracts with missing IB "
                     f"details in master listing.")

    def __connect_tws(self) -> None:
        """Docstring"""
        self.mediator.notify("connect_to_tws")
        logging.info(f"Connnected to TWS.")

    def __disconnect_tws(self) -> None:
        """Docstring"""
        self.mediator.notify("disconnect_from_tws")
        logging.info(f"Disconnnected from TWS.")

    def __check_abort_conditions(self) -> bool:
        if self.mediator.notify("exit_signal"):
            logging.info(f"Ctrl-C detected. Abort fetching of IB "
                         "details.")
            return True
        elif self.mediator.notify("tws_has_error"):
            logging.info(f"TWS error detected. Abort fetching of IB "
                         "details.")
            return True
        else:
            return False

    def __get_contract_details_from_tws(self, contract: Any) -> None:
        """Docstring"""

        parameters = {
            'contract_type_from_listing': contract['contract_type_from_listing'],
            'broker_symbol': contract['broker_symbol'],
            'exchange': contract['exchange'],
            'currency': contract['currency']}
        details = self.mediator.notify(
            "download_contract_details_from_tws", parameters)
        if len(details) == 0:
            raise QueryReturnedNoResultError
        elif len(details) > 1:
            raise QueryReturnedMultipleResultsError
        else:
            self.__details = details[0]

    def __decode_exchange_names(self) -> None:
        """Docstring"""

        for ex in [self.__details.contract.exchange,
                   self.__details.contract.primaryExchange]:
            ex = self.mediator.notify("decode_exchange_ib", {'exchange': ex})

    def __insert_ib_details_into_db(self, contract: Any) -> None:
        """Docstring"""

        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()
        cur.execute("""
            REPLACE INTO contract_details_ib (
                contract_id,
                contract_type_from_details,
                primary_exchange,
                industry,
                category,
                subcategory)
                VALUES (?, ?, ?, ?, ?, ?)""", (
            contract['contract_id'],
            self.__details['contract_type_from_details'],
            self.__details['primary_exchange'],
            self.__details['industry'],
            self.__details['category'],
            self.__details['subcategory)']))
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

    def update_ib_contract_details(self):
        """Docstring"""

        self.__get_contracts()
        self.__setup_progress_bar()
        self.__connect_tws()
        try:
            for contract in self.__contracts:
                if self.__check_abort_conditions():
                    break
                try:
                    self.__get_contract_details_from_tws(contract)
                except (QueryReturnedNoResultError, QueryReturnedMultipleResultsError):
                    pass
                else:
                    self.__decode_exchange_names()
                    self.__insert_ib_details_into_db(contract)
                finally:
                    self.__pbar.update(inc=1)
        finally:
            self.__disconnect_tws()
