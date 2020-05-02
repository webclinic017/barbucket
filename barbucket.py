from barbucket.contracts_db import ContractsDB
from barbucket.quotes_db import QuotesDB
from barbucket.tws_connector import TwsConnector
from barbucket.data_quality_check import DataQualityCheck


cont_db = ContractsDB()
quot_db = QuotesDB()
tws_conn = TwsConnector()
dq_check = DataQualityCheck()


# cont_db.init_database()

# stock_exchanges = ["nasdaq", "nyse", "amex", "arca"]
exchanges = ["nasdaq"]
ctype = "STOCK"
# # etf_exchanges = ["fwb", "ibis", "lse", "lseetf"]
# exchanges = ["fwb"]
# ctype = "ETF"
for ex in exchanges:
    cont_db.sync_contracts_to_listing(ctype=ctype, exchange=ex)

# tws_conn.get_historical_data()

# dq_check.handle_single_contract(contract_id=108)

# dq_check.get_trading_calendar("FWB")