# Contract details from Tradingview
Additional details for the existing contracts can be added from the free [Tradingview](https://tradingview.com) stock screener.

## Download .csv files
* Go to [https://www.tradingview.com/chart](https://www.tradingview.com/chart)
* On the bottom left, open the stock screener panel
* Select a country and set filters as you like
* Set the screener coulmns to:
    * `Average Volume (30 day)`
    * `Country`
    * `Exchange`
    * `Gross Profit (FY)`
    * `Market Capitalization`
    * `Number of Employees`
    * `Simple Moving Average (30)`
    * `Total Revenue (FY)`
* Save the coulmn set for convenience
* Download the screener results as `.csv` file
* Repeat for other countries if necessary

## Add details to database
* Place all downloaded `.csv` files into the folder `~/.barbucket/tv_screener`
* Then execute:
```console
$ barbucket contracts read-tv-details
```
* For each contract in each .csv-file the software will try to find a corresponding contract in your database and add the screener details.
 
 