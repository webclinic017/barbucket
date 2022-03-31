# Sync exchange listings
You can sync your local listing of available contracts to IB's exchange listing.

```console
$ barbucket contracts sync-listing --type STOCK --exchange NYSE
```
`--type` can be `STOCK` or `ETF`<br>
`--exchange` can be the code for any exchange available on IB

> Syncing actually means, that: <br>
> * Contracts from the exchange listing, that do not exist in your local database, will be added to the database.<br>
> * Local contracts, that do not exist in the exchange listing, will be deleted locally.
