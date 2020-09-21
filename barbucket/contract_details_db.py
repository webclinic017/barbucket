import sqlite3
import os
from pathlib import Path
import pandas as pd

from barbucket.database import DataBase
from barbucket.contracts_db import ContractsDB


class ContractTwDetailsDB(DataBase):

    def __init__(self):
        self.__contracts_db = ContractsDB()



    def __encode_exchange(self, exchange):
        exchange_codes = {
            'NASDAQ': "ISLAND",     # NASDAQ / Island
            'ISLAND': "ISLAND",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'ARCA': "NYSE ARCA",    # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'IBIS': "XETR",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]



    def __decode_exchange(self, exchange):
        exchange_codes = {
            'ISLAND': "NASDAQ",     # NASDAQ / Island
            'NASDAQ': "NASDAQ",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'NYSE ARCA': "ARCA",    # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'XETR': "IBIS",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]



    def __insert_tw_details(self, contract_id, market_cap, avg_vol_30_in_curr,
            country, employees, profit, revenue):

        conn = self.connect()
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
        self.disconnect(conn)



    def insert_new_entry(self, contract_id):
        self.__insert_tw_details(
            contract_id=contract_id,
            market_cap="NULL",
            avg_vol_30_in_curr="NULL",
            country="NULL",
            employees="NULL",
            profit="NULL",
            revenue="NULL")



    def ingest_tw_files(self):
        mypath = Path.home() / ".barbucket/tw_screener"
        screener_files = [f for f in os.listdir(mypath) if
            os.path.isfile(os.path.join(mypath, f))]

        # Iterate over files in directory
        for file in screener_files:
            if file.startswith("Done_"):
                continue

            # Read file
            df = pd.read_csv(mypath / file, sep=",")

            # Iterate over rows
            for _, row in df.iterrows():

                # Find corresponding contract id
                ticker = row["Ticker"].replace(".", " ")
                filters = {'primary_exchange': self.__decode_exchange(row["Exchange"]),
                    'contract_type_from_listing': "STOCK",
                    'exchange_symbol': ticker}
                columns = ['contract_id']
                result = self.__contracts_db.get_contracts(
                    filters=filters,
                    return_columns=columns)

                if len(result) == 1:
                    # Prepare the data
                    contract_id = result[0]["contract_id"]

                    avg_vol_30_in_curr = row["Average Volume (30 day)"] * \
                        row["Simple Moving Average (30)"]
                    if pd.isna(avg_vol_30_in_curr):
                        avg_vol_30_in_curr = 0
                    else:
                        avg_vol_30_in_curr = int(avg_vol_30_in_curr)

                    if pd.isna(row["Number of Employees"]):
                        employees = 0
                    else:
                        employees = int(row["Number of Employees"])

                    if pd.isna(row["Gross Profit (FY)"]):
                        profit = 0
                    else:
                        profit = int(row["Gross Profit (FY)"])
                        
                    if pd.isna(row["Total Revenue (FY)"]):
                        revenue = 0
                    else:
                        revenue = int(row["Total Revenue (FY)"])
                        
                    # Write details to db
                    self.__insert_tw_details(
                        contract_id=contract_id,
                        market_cap=row["Market Capitalization"],
                        avg_vol_30_in_curr=avg_vol_30_in_curr,
                        country=row["Country"],
                        employees=employees,
                        profit=profit,
                        revenue=revenue)
                else:
                    ticker =row["Ticker"]
                    exchange = row["Exchange"]
                    print(f"Error: {len(result)} results for {ticker} \
                        on {exchange}.")

            # Rename file
            os.rename(mypath / file, mypath / ("Done_" + file))


