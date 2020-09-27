import pandas as pd

from barbucket.database import DatabaseConnector


class TvDetailsDatabase():

    def __init__(self):
        pass


    def insert_tv_details(self, contract_id, market_cap, avg_vol_30_in_curr,
        country, employees, profit, revenue):

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""REPLACE INTO contract_details_tv (
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
            row_formated['market_cap'] = int(row['Market Capitalization'])

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
