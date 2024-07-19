# utencilios

[![Documentation Status](https://readthedocs.org/projects/utencilios/badge/?version=latest)](https://utencilios.readthedocs.io/en/latest/?badge=latest)

A collection of useful code for working with data. `utencilios` is the spanish word for utensils.

## Dev Tips

First create your venv using `requirements.txt`, then activate it and install this package with:
```
$ pip install -e .
```

Run tests (after activating the virtual environment)
```
$ python -m pytest
$ pytest -rP
```

## Buildings docs locally

First make sure you have `make` installed, if you're on windows you can download it here: https://chocolatey.org/install

Then, create and activate a _new_ virtual environment using `requirements.txt` in the `docs/` directory. Then run this from inside the `docs` directory:
```
$ make clean html
```

### Distributing

To create distribution archives
```
$ python3 -m pip install --upgrade build
$ python3 -m build
```

To upload package to test pypi
```
$ python3 -m twine upload -r testpypi dist/*
```

https://packaging.python.org/en/latest/