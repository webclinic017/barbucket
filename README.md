# Barbucket 🪣
## _A database for financial contracts and pricing data_
<br>

![python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![sqlite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![postgres](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
<br>

![commits](https://badgen.net/github/commits/croidzen/barbucket)
![last_commit](https://badgen.net/github/last-commit/croidzen/barbucket)
![prs](https://img.shields.io/github/issues-pr-closed/croidzen/barbucket.svg)
![issues_open](https://img.shields.io/github/issues/croidzen/barbucket.svg)
![issues_closed](https://img.shields.io/github/issues-closed/croidzen/barbucket.svg)
![license](https://img.shields.io/github/license/croidzen/barbucket.svg)
![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
<br>

![documentation](https://readthedocs.org/projects/barbucket/badge/)
![pypi_version](https://badgen.net/pypi/v/barbucket)<br>
![code_check workflow](https://github.com/croidzen/barbucket/actions/workflows/code_check.yml/badge.svg)
![deploy workflow](https://github.com/croidzen/barbucket/actions/workflows/deploy.yml/badge.svg)
<br>

## Features
* Syncing contracts of IB's exchange listings to a local database
* Adding fundamental data from Tradringview's screener
* Creating groups of contracts (universes)
* Downloading daily historical quotes using IB's TWS API (paid market data subscriptions on IB are necessary)
* Storage of downloaded quotes into a local database for fast access

## Supported contract types
* Stocks
* ETFs
* Crypto currencies (planned)

## Supported DBMS
* PostgreSQL
* SQLite
* MySQL / MariaDB
* MS SQL Server
* Oracle
* [and even more](https://docs.sqlalchemy.org/en/14/dialects/)

## Supported APIs
* [Intercative Brokers](http://interactivebrokers.com) TWS API
* [Tradingview](https://tradingview.com)-Screener .csv files
* [EOD Historical Data](https://eodhistoricaldata.com) (planned)
* [CCXT](https://github.com/ccxt/ccxt) (planned)

## Tech stack
For an overview of how this project is realized, please see the [contributing](https://github.com/croidzen/barbucket/blob/master/CONTRIBUTING.md) document.

## Full documentation
[https://barbucket.readthedocs.io](https://barbucket.readthedocs.io/)

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

## Status
* Early beta stage. Expect code- and data-breaking modifications
* Aimed at software developers. Knowlede about how to handle a database is necessary to use this software
