import sqlite3

from barbucket.database import DataBase


class ContractDetailsDB(DataBase):

    def __init__(self):
        pass


    def insert_contract_details(self, contract_id, industry, category,
        subcategrory, ib_con_id, primary_exchange, stock_type):

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""REPLACE INTO contract_details (contract_id, industry,
            category, subcategrory, ib_con_id, primary_exchange, stock_typus) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (contract_id, industry, category,
            subcategrory, ib_con_id, primary_exchange, stock_type))

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def get_contract_details(self, contract_id):

        query = f"""SELECT contract_id, industry, category, subcategrory,
                        ib_con_id, primary_exchange, stock_typus
                    FROM contract_details
                    WHERE contract_id = {contract_id};"""

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        if len(result) > 0:
            return result[0]
        else:
            return None
