# Installation
## Requirements
* Linux or macOS; Windows is not fully tested yet
* Python >= 3.7

## Install with pip
Using virtual environments for Python is strongly recommented. See [venv](https://docs.python.org/3/library/venv.html). Then install with:
```console
$ pip install barbucket
```

## Install with pipenv
Using virtual environments for Python is strongly recommented. See [pipenv](https://pipenv.pypa.io/en/latest/). Then install with:
```console
$ pipenv install barbucket
```

## Check installation
Check if the installation was successfull:
```console
$ barbucket --help

Usage: barbucket [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose  -v for DEBUG
  --help         Show this message and exit.

Commands:
  contracts  Contracts commands
  quotes     Quotes commands
  universes  Universes commands
```
