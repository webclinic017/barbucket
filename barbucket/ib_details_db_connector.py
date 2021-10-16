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
        """Insert contract details into db"""

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
