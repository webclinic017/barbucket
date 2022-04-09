# Contributing
🎉 Thank you for considering to contribute to Barbucket. All contributions are welcome! ❤️

## Class diagram
A [UML class diagram](https://github.com/croidzen/barbucket/blob/master/resources/class_diagram.png) is available within the repository.

## Task management
See [Issues](https://github.com/croidzen/barbucket/issuesv) on Github project page.

## Python
- Virtual environments with `Pipenv` or `venv`
- Package management with `Pipenv` or `Pip`

## Codestyle
- Validation is automated in CI pipeline with Github-Actions
- Pep8 formatting, checked by `Autopep8`
- Using Python type hints, checked by `Mypy`

## Unittests
- Testing is automated in CI pipeline with Github-Actions
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
- Package build und PyPI uplodad are automated in CI pipeline with Github-Actions
- Version number is handled manually in 'setup.cfg'
- Manual build `$ python -m build` and upload `$ twine upload dist/*` (credentials prompted) still posssible

## Setting up a dev environment
- Clone the repo: `$ git clone https://github.com/croidzen/barbucket .`
- Change to repo dir: `$ cd barbucket`
- Create a virtual environment: `$ pipenv shell`
- Install dependencies: `$ pipenv install --dev`
