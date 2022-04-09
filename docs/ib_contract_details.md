# Add contract details from Interactive Brokers
You can download the details data from Interactive Brokers for all contracts in the database, where these details are not yet present. The data is collected from the TWS API, so TWS needs to be running and the API active. No market data subscription from IB is necessary.

```console
$ barbucket contracts download-ib-details
```

These informations are then stored to the database:

* Stock type
* Primary exchange
* Industry
* Category
* Subcategory

As none of IB's speedlimits applies for downloading contract details, this operation is quite fast, even for a large ammount of contracts.
