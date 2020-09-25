import os
from pathlib import Path
import pandas as pd

from barbucket.database import DatabaseConnector
from barbucket.contracts import ContractsDatabase
from barbucket.tools import Tools


class TvDetailsDatabase():

    def __init__(self):
        pass


    def insert_tw_details(self, contract_id, market_cap, avg_vol_30_in_curr,
        country, employees, profit, revenue):

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""REPLACE INTO contract_details_tw (
            contract_id,
            market_cap,
            avg_vol_30_in_curr,
            country,
            employees,
            profit,
            revenue) 
            VALUES (?, ?, ?, ?, ?, ?, ?)""", (
            contract_id,
            market_cap,
            avg_vol_30_in_curr,
            country,
            employees,
            profit,
            revenue))

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)


    def insert_new_entry(self, contract_id):
        self.insert_tw_details(
            contract_id=contract_id,
            market_cap="NULL",
            avg_vol_30_in_curr="NULL",
            country="NULL",
            employees="NULL",
            profit="NULL",
            revenue="NULL")



class TvDetailsFile():

    def __init__(self):
        pass


    def get_data_from_file(self, file):

        # Read file
        df = pd.read_csv(file, sep=",")
        file_data = []

        # Iterate over rows
        for _, row in df.iterrows():

            row_formated = {}
            
            # Prepare the data
            row_formated['ticker'] = row['Ticker']
            row_formated['exchange'] = row['Exchange']
            row_formated['market_cap'] = row['Market Capitalization']

            avg_vol_30_in_curr = row["Average Volume (30 day)"] * \
                row["Simple Moving Average (30)"]
            if pd.isna(avg_vol_30_in_curr):
                row_formated['avg_vol_30_in_curr'] = 0
            else:
                row_formated['avg_vol_30_in_curr'] = int(avg_vol_30_in_curr)

            row_formated['country'] = row['Country']

            if pd.isna(row["Number of Employees"]):
                row_formated['employees'] = 0
            else:
                row_formated['employees'] = int(row["Number of Employees"])

            if pd.isna(row["Gross Profit (FY)"]):
                row_formated['profit'] = 0
            else:
                row_formated['profit'] = int(row["Gross Profit (FY)"])
                
            if pd.isna(row["Total Revenue (FY)"]):
                row_formated['revenue'] = 0
            else:
                row_formated['revenue'] = int(row["Total Revenue (FY)"])

            file_data.append(row_formated)

        return file_data



class TvDetails():

    def __init__(self):
        pass


    def ingest_tw_files(self):
        # Instanciate necessary objects
        tv_details_db = TvDetailsDatabase()
        tv_details_file = TvDetailsFile()
        contracts_db = ContractsDatabase()
        tools = Tools()
        
        # Create list of path+filename of all files in directory
        dir_path = Path.home() / ".barbucket/tw_screener"
        screener_files = [
            os.path.join(dir_path, f) for f in os.listdir(dir_path) if
            os.path.isfile(os.path.join(dir_path, f))]

        # Iterate over files in directory
        for file in screener_files:
            file_data = tv_details_file.get_data_from_file(file=file)

            for row in file_data:
                # Find corresponding contract id
                ticker = row['ticker'].replace(".", " ")
                filters = {'primary_exchange': tools.decode_exchange(row['exchange']),
                    'contract_type_from_listing': "STOCK",
                    'exchange_symbol': ticker}
                columns = ['contract_id']
                result = contracts_db.get_contracts(
                    filters=filters,
                    return_columns=columns)

                if len(result) == 1:

                    # Write details to db
                    contract_id = result[0]['contract_id']
                    tv_details_db.insert_tw_details(
                        contract_id=contract_id,
                        market_cap=row['market_cap'],
                        avg_vol_30_in_curr=row['avg_vol_30_in_curr'],
                        country=row['country'],
                        employees=row['employees'],
                        profit=row['profit'],
                        revenue=row['revenue'])
                else:
                    ticker =row['ticker']
                    exchange = row['exchange']
                    print(f"Error: {len(result)} results for {ticker} \
                        on {exchange}.")


