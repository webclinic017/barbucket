# Barbucket
Loading and storing historical price data of financial contracts

## Features
* Syncing local contracts database to IB's exchange listing
* Adding fundamental data to local contracts database from Tradringview's screener
* Creating groups of contracts (universes)
* Downloading daily historical quotes for universes using IB's TWS API (market data subscriptions on IB are necessary)
* Storage of downloaded quotes in a local database

## Installation
* Clone the project to your machine
* Use the pipfile to setup a virtual python environment
* Run 'pyton barbucket --help' to check if everything is working
* Refer to the documentation for further usage

## Status
* Early alpha stage. Expect code- and data breaking modifications
* Aimed at software developers. Knowlede about how to handle a databse is necessary to use this software

## Documentation
* [barbucket.rtfd.io](http://barbucket.rtfd.io/)

## Contributing
* Feature requests, bug reports and code contributions are welcome, please create an issue or contact me