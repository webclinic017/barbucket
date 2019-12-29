from data_management.contracts_db import ContractsDB
from data_management.quotes_db import QuotesDB

import data_management.req_historical_data
import data_management.data_quality_check


cont_db = ContractsDB()
quot_db = QuotesDB()

# cont.init_database()
# cont.migrate_from_contracts_db()

# cont.delete_no_data_contracts()

# exchanges = ['fwb', 'ibis', 'lse', 'lseetf']
# for ex in exchanges:
#     cont.sync_contracts_to_listing(ex)

# cont.sync_contracts_to_listing('fwb')

# data_management.req_historical_data.get_historical_data()

quot_db. migrate_from_csv()