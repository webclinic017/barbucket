## Branches

## Versioning

## Documentation
### Build
* Is done by readthedocs after receiving webhook request.
* Can be done locally with: `$ docs/make html` but result is excluded from git.

### Upload
* https://readthedocs.org/projects/barbucket/
* Github webhook is triggered on certain events. RTD receives the request and pulls the pre-built documentation files.

## Package
### Local pre-build testing
* `$ pip install <barbucket_project_directory> -e`

### Build
* `$ python -m build`

### Upload
* `$ twine upload dist/*`
* Username and password will be prompted