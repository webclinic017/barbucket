Universes
=========

To conveniently handle the contracts, you can group them to universes.

| Listing all existing universes
|    ``python barbucket univeses list``

| Creating a new universe
|    ``python barbucket universes create --name my_universe --contract_ids 1,2,3``
|    The ``contracts_ids`` are automatically assigned to the contracts by the software on their creation and need to be obtained manually from the database.

| Getting all members of a universe
|    ``python barbucket universes members --name my_universe``

| Deleting a universe
|    ``python barbucket universes delete --name my_universe``