import logging

import enlighten

from .mediator import Mediator


class IbDetailsProcessor():
    """Docstring"""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__contracts = []

    def __get_contracts(self):
        """Get contracts from db, where IB details are missing"""

        columns = ['contract_id', 'contract_type_from_listing',
                   'broker_symbol', 'exchange', 'currency']
        filters = {'primary_exchange': "NULL"}
        parameters = {'filters': filters, 'return_columns': columns}
        self.__contracts = self.mediator.notify(
            self, "get_contracts", parameters)
        logging.info(f"Found {len(self.__contracts)} contracts with missing IB "
                     f"details in master listing.")

    def __connect_tws(self):
        self.tws.connect()
        logging.info(f"Connnected to TWS.")

    def __disconnect_tws(self):
        self.tws.disconnect()
        logging.info(f"Disconnnected from TWS.")

    def __get_contract_details_from_tws(self, contract):
        contract_details = self.tws.download_contract_details(
            contract_type_from_listing=contract['contract_type_from_listing'],
            broker_symbol=contract['broker_symbol'],
            exchange=contract['exchange'],
            currency=contract['currency'])

    def __insert_ib_details_into_db(self, contract_id, contract_type_from_details,
                                    primary_exchange, industry, category,
                                    subcategory):
        """Docstring"""

        conn = self.mediator.notify(self, "get_db_connection", {})
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
            contract_id,
            contract_type_from_details,
            primary_exchange,
            industry,
            category,
            subcategory))
        conn.commit()
        cur.close()
        self.mediator.notify(self, "close_db_connection", {'conn': conn})

    def fetch_ib_contract_details(self):
        """Docstring"""

        self.__get_contracts()

        # Setup progress bar
        manager = enlighten.get_manager()
        pbar = manager.counter(
            total=len(contracts),
            desc="Contracts", unit="contracts")

        self.__connect_tws()

        try:
            for contract in self.__contracts:
                # Check for abort conditions
                if self.exiter.exit() or self.tws.has_error():
                    logging.info(f"Abort fetching of IB details.")
                    break

                self.__get_contract_details_from_tws(contract)

                # Catch no details returned

                self.__insert_ib_details_into_db(
                    contract_id=contract['contract_id'],
                    contract_type_from_details=contract_details.stockType,
                    primary_exchange=contract_details.contract.primaryExchange,
                    industry=contract_details.industry,
                    category=contract_details.category,
                    subcategory=contract_details.subcategory)

                pbar.update()

        finally:
            self.__disconnect_tws()
