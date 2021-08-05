from barbucket.database import DatabaseConnector


class IbDetailsDatabase():

    def __init__(self):
        pass

    def insert_ib_details(self, contract_id, contract_type_from_details,
                          primary_exchange, industry, category, subcategory):

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
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
        db_connector.disconnect(conn)
