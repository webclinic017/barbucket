# Sync exchange listings
You can sync your local listing of available contracts to IB's exchange listing:

- Contracts from the exchange listing, that do not exist in your database, will be added to the database.
- Contracts from your database, that do not exist in the exchange listing, will be deleted in your database.

```console
$ barbucket contracts sync-listing --type STOCK --exchange NYSE
```
| Option | Description |
| ------ | ----------- |
| `-t`, `--type`| can be `STOCK` or `ETF` |
| `-e`, `--exchange`| can be the code for any exchange available on IB |
