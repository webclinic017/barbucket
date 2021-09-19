import logging
from typing import Any

from .mediator import Mediator
from .base_component import BaseComponent

logger = logging.getLogger(__name__)


class IbDetailsConnector(BaseComponent):
    """Provides methods to access the 'ib_details' table of the database."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def insert_ib_details(self, contract_id: str,
                          contract_type_from_details: str,
                          primary_exchange: str, industry: str, category: str,
                          subcategory: str) -> None:
        """Insert contract details into db"""

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
                    contract_id,
                    contract_type_from_details,
                    primary_exchange,
                    industry,
                    category,
                    subcategory))
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.debug(f"Inserted IB details into db: {contract_id} "
                     f"{contract_type_from_details} {primary_exchange} "
                     f"{industry} {category} {subcategory}")
