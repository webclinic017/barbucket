# Cli usage examples / shortcuts

database_archive:
	python barbucket.py database archive

contracts_sync-listing:
	python barbucket.py contracts sync-listing --type STOCK --exchange NYSE

contracts_fetch-ib-details:
	python barbucket.py contracts fetch-ib-details

contracts_fetch-tv-details:
	python barbucket.py contracts fetch-tv-details

universes_create:
	python barbucket.py universes create --name test_univ --contract_ids 1,2,3

universes_list:
	python barbucket.py universes list

universes_members:
	python barbucket.py universes members --name test_univ

universes_delete:
	python barbucket.py universes delete --name test_univ

quotes_fetch:
	python barbucket.py quotes fetch --universe germany_top_800_cap