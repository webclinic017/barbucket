from data_management.contracts_db import ContractsDB
from data_management.quotes_db import QuotesDB
from data_management.tws_connector import TwsConnector
from data_management.data_quality_check import DataQualityCheck


cont_db = ContractsDB()
quot_db = QuotesDB()
tws_conn = TwsConnector()
dq_check = DataQualityCheck()


# cont_db.init_database()

# exchanges = ['fwb']
# exchanges = ['fwb', 'ibis', 'lse', 'lseetf']
# for ex in exchanges:
#     cont_db.sync_contracts_to_listing(ctype='ETF', exchange=ex)

# cont_db.sync_contracts_to_listing(ctype='ETF', exchange='fwb')

tws_conn.get_historical_data()

# dq_check.handle_single_contract(contract_id=108)

# dq_check.get_trading_calendar('FWB')