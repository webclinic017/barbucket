# Quickstart

## Install
```console
$ pip install barbucket
```
For more details on installing Barbucket, see [installation](installation.md)

## Sync contracts to listing
```console
$ barbucket contracts sync-listing --type STOCK --exchange NYSE
```
For more details on syncing contracts to an exchange listing, see [Synchronize contracts](sync_contracts.md)

## Create trading universe
```console
$ barbucket universes create --name my_universe --contract_ids 1,2,3
```
For more details on trading universes, see [Universes](universes.md)

## Download quotes
```console
$ barbucket quotes download --universe my_universe
```
For more details on downloading quotes, see [Quotes](quotes.md)
