 # tws_connector
    - encode
    - decode
    - connect
    - disconnect
    - get_histo_Data
    - get_details
# contract_details
    - encode
    - decode
    - insert_details
    - insert_new_entry
    - (user_called) ingest_tw_files -> contracts
# universes
    - create_membership
    - (user_called) create_universe
    - (user_called) get_universes
    - (user_called) get_universe_menbers
    - (user_called) delete universe
# quotes
    - insert_quotes
    - (user_called) get_quotes
    - delete_quotes
    - get_quotes_status
    - update_quotes_status
    - (user_called) download_quotes -> universes, tws_connector, contracts
# contracts
    - create_contract -> tws_connector
    - (user_called) get_contracts
    - delete_contract
    - read_ib_listing
    - (user_called) sync_contracts_to_listing


