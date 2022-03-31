# Contributing
🎉 Thank you for considering to contribute to Barbucket. All contributions are welcome! ❤️

## Class diagram
A [UML class diagram](https://github.com/croidzen/barbucket/blob/master/resources/class_diagram.png) is available within the repository.

## Task management
See [Issues](https://github.com/croidzen/barbucket/issuesv) on Github project page.

## Python
- Virtual environments with `Pipenv` or `venv`
- Package manament with `Pipenv` or `Pip`

## Codestyle
- Pep8 formatting, checked by `Autopep8`
- Using Python type hints, checked by `Mypy`

## Unittests
- Framework: `Pytest`
- Located at: `tests/`
- Running tests: `$ pytest`
- Code coverage: `$ pytest --cov=barbucket`

## Documentation
- Framework: `Mkdocs`
- Located at `docs/`
- Local testing with: `mkdocs serve`
- Building and uploading to [readthedocs](https://barbucket.readthedocs.io/) is automated with Github webhook on push to `master` branch.

## PyPI package
- Build package with: `$ python -m build`
- Upload with: `$ twine upload dist/*` (Username and password will be prompted)

## Setting up a dev environment
- Clone the repo: `$ git clone https://github.com/croidzen/barbucket .`
- Change dir to repo: `$ cd barbucket`
- Create a virtual environment: `$ pipenv shell`
- Install dependencies: `$ pipenv install`
