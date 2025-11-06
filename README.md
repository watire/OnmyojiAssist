# OnmyojiAssist

OnmyojiAssist automates common gameplay loops in Onmyoji with a PyQt5 desktop interface and computer-vision helpers.

## Running tests

The project uses `pytest` with coverage reporting. Install the dependencies listed in `requirements.txt` and execute:

```bash
python -m pytest
```

This command will run the test suite, collect coverage data for the helper modules, and produce a `coverage.xml` report in the project root.

## CI status

[![CI](https://github.com/<owner>/<repo>/actions/workflows/python-app.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/python-app.yml)

Automated Windows builds are configured via GitHub Actions to install dependencies, run the test suite, and upload the coverage report artifact on pushes and pull requests.
