from data_management.contracts_db import ContractsDB
from data_management.quotes_db import QuotesDB
from data_management.tws_connector import TwsConnector
from data_management.data_quality_check import DataQualityCheck


cont_db = ContractsDB()
quot_db = QuotesDB()
tws_conn = TwsConnector()
dq_check = DataQualityCheck()


# cont_db.init_database()
# cont_db.migrate_from_contracts_db()

# cont_db.delete_bad_status_contracts()

# exchanges = ['fwb', 'ibis', 'lse', 'lseetf']
# for ex in exchanges:
#     cont_db.sync_contracts_to_listing(ex)

# cont_db.sync_contracts_to_listing('fwb')

# tws_conn.get_historical_data()

# quot_db. migrate_from_csv()

dq_check.check_quotes_data_quality()