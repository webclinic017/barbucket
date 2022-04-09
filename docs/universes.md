# Universes
To conveniently handle the contracts, you can group them to universes.

## Listing all existing universes
```console
$ barbucket universes list
```

## Creating a new universe
```console
$ barbucket universes create --name my_universe --contract_ids 1,2,3
```
| Option | Description |
| ------ | ----------- |
| `-n`, `--name` | Name of the universe to create |
| `-c`, `--contract_ids` | The ``contracts_ids`` are automatically assigned to the contracts by the software on their creation and need to be obtained manually from the database. |
 
## Deleting a universe
```console
$ barbucket universes delete --name my_universe
```
| Option | Description |
| ------ | ----------- |
| `-n`, `--name` | Name of the universe to delete |
