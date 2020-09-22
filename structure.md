# contracts_handler
- create_contract -> tws_connector
- get_contracts
- sync_contracts_to_listing
## contracts_db_hanlder
- create_contract
- get_contracts
- delete_contract
## ib_listings_handler
- read_ib_listing

# tv_details_hadler
- ingest_tw_files -> contracts
## tv_details_db_handler
- insert_details
- create_empty_entry
## tv_details_file_handler
- get_data_from_file

# quotes-hanlder
- download_quotes -> universes, tws_connector, contracts
## quotes_db_handler
- insert_quotes
- get_quotes
- delete_quotes
## quotes_status_db_handler
- create_empty_quote_status
- get_quotes_status
- update_quotes_status

# tws_connector
- connect
- disconnect
- get_histo_data
- get_details

# universes_db_handler
- create_membership
- create_universe
- get_universes
- get_universe_members
- delete universe

# tools
- encode
- decode