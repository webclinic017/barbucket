# Barbucket

![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![sqlite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![license](https://img.shields.io/github/license/croidzen/barbucket.svg)
![issues_open](https://img.shields.io/github/issues/croidzen/barbucket.svg)
![issues_closed](https://img.shields.io/github/issues-closed/croidzen/barbucket.svg)
![commits](https://badgen.net/github/commits/micromatch/micromatch)
![last_commit](https://badgen.net/github/last-commit/micromatch/micromatch)
![pypi_version](https://badgen.net/pypi/v/barbucket)

A local database for financial contracts and pricing data

## Features
* Syncing contracts of IB's exchange listings to a local database
* Adding fundamental data from Tradringview's screener
* Creating groups of contracts (universes)
* Downloading daily historical quotes using IB's TWS API (paid market data subscriptions on IB are necessary)
* Storage of downloaded quotes into a local database for fast access

## Quickstart
Installation:
```console
$ pip install barbucket
```
Sync contracts:
```console
$ barbucket contracts sync-listing --type stock --exchange nasdaq
```
See results at:
```console
~/.barbucket/database.sqlite
```

## Requirements
* Linux or macOS; Windows is not tested yet
* Python >= 3.7

## Asset types
* Stocks
* ETFs
* Crypto currencies (planned)

## DBMS
* SQLite
* PostgreSQL (planned)

## APIs
* [Intercative Brokers](http://interactivebrokers.com) TWS API
* [Tradingview](https://tradingview.com) screener .csv files
* [EOD Historical Data](https://eodhistoricaldata.com) (planned)
* [CCXT](https://github.com/ccxt/ccxt) (planned)

## Status
* Early beta stage. Expect code- and data-breaking modifications
* Aimed at software developers. Knowlede about how to handle a database is necessary to use this software

## Full documentation
* [barbucket.rtfd.io](http://barbucket.rtfd.io/)
