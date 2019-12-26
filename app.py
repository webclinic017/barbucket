import data_management.contracts
import data_management.histo
import data_management.data_quality_check


con = data_management.contracts.ContractsDB()

# con.init_database()
# con.create_contract('test', 'This is ma name', 'USD', 'TOY_X')
# result = con.get_contracts(exchange='LSEETF')
# print((result[0])['symbol'])
# con.import_from_tinydb()
# con.delete_no_data_contracts()

# exchanges = ['fwb', 'ibis', 'lse', 'lseetf']
# for ex in exchanges:
#     con.sync_contracts_to_listing(ex)

# con.sync_contracts_to_listing('fwb')


data_management.histo.get_historical_data()