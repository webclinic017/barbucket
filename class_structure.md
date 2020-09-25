# Application
(group database)
+ reset_database -> Database
(group contracts)
+ get_contracts -> Contracts
+ sync_contracts_to_listing -> Contracts
(group tv_details)
+ ingest_tw_files -> TvDetails
(group quotes)
+ fetch_historical_quotes -> Quotes
+ get_quotes -> Quotes
(group universes)
+ create_universe -> Universes
+ get_universes -> Universes
+ get_universe_members -> Universes
+ delete universe -> Universes

## Database
+ init_database -> DatabaseConnector
#### DatabaseConnector
+ connect
+ disconnect

## Contracts
+ get_contracts -> ContractsDatabase
+ sync_contracts_to_listing- > ContractsDatabase, IbExchangeListings
- create_contract -> ContractsDatabase, Tws, TvDetailsDatabase, QuotesStatusDatabase
### ContractsDatabase
+ create_contract
+ get_contracts
+ delete_contract
### IbExchangeListings
+ read_ib_listing

## TvDetails
+ ingest_tw_files -> TvDetailsDatabase, TvDetailsFiles, ContractsDatabase
### TvDetailsDatabase
+ create_empty_entry
+ insert_details
### TvDetailsFile
+ get_data_from_file

## Quotes
+ fetch_historical_quotes -> QuotesDatabase, QuotesStatusDatabase, Universes, Tws, ContractsDatabase
+ get_quotes -> QuotesDatabase
### QuotesDatabase
+ insert_quotes
+ get_quotes
- delete_quotes
### QuotesStatusDatabase
+ create_empty_quote_status
+ get_quotes_status
+ update_quotes_status

### Tws
+ download_historical_quotes
+ download_contract_details
- connect
- disconnect

### Universes
+ create_universe
+ get_universes
+ get_universe_members
+ delete universe
- create_membership

#### Tools
+ encode
+ decode
