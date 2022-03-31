# Contributing

🎉 Thank you for considering to contribute to Barbucket. All contributions are welcome! ❤️

## Project information
class diagram
## Codestyle
type hints
formatting

## Setup dev environment

## Contributions workflow
issues
branches
tests
pr
versioning
build
deploy

## Documentation
### Build
* Is done by readthedocs after receiving webhook request.
* Can be done locally with: `$ docs/make html`, result is excluded from git.
## Upload
* https://readthedocs.org/projects/barbucket/
* Github webhook is triggered on certain events. RTD receives the request and builds the docs itself.

## CI/CD
    deployment
    documentation
    format, lint
    test

## Python package
### Build
* `$ python -m build`
deployment
### Upload
* `$ twine upload dist/*`
* Username and password will be prompted

## Testing
### Unittests
location
execution
man: pytest
cicd
coverage

### Integration tests
Not automated yet, is done manually
* `$ pip install <barbucket_project_directory> -e`

