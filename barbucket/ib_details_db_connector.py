import logging

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class IbDetailsDbConnector(DbConnector):
    """Provides methods to access the 'ib_details' table of the database."""

    def __init__(self) -> None:
        super().__init__()

    def insert_ib_details(self, contract_id: str,
                          contract_type_from_details: str,
                          primary_exchange: str, industry: str, category: str,
                          subcategory: str) -> None:
        """Insert contract details into db

        :param contract_id: Contract ID of the contract
        :type contract_id: str
        :param contract_type_from_details: Type of the contract
        :type contract_type_from_details: str
        :param primary_exchange: Primary exchange of the contract
        :type primary_exchange: str
        :param industry: Industry classification of the contract
        :type industry: str
        :param category: Category classification of the contract
        :type category: str
        :param subcategory: Subcategory classification of the contract
        :type subcategory: str
        """

        conn = self.connect()
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
        self.disconnect(conn)
        logger.debug(f"Inserted IB details into db: {contract_id} "
                     f"{contract_type_from_details} {primary_exchange} "
                     f"{industry} {category} {subcategory}")
