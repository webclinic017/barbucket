# Contract details from IB
Downloads additional information for existing contracts from IB over the TWS

```console
$ barbucket contracts download-ib-details
```

This will downlad the details data for all contracts in the database, where these details are not yet present.

These informations are then stored to the database:
* Stock type
* Primary exchange
* Industry
* Category
* Subcategory

As none of IB's speedlimits applies for downloading contract details, this operation is quite fast, even for a large ammount of contracts.
