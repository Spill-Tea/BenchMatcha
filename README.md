# PyTemplate
[![build status][buildstatus-image]][buildstatus-url]

[buildstatus-image]: https://github.com/Spill-Tea/PyTemplate/actions/workflows/python-app.yml/badge.svg?branch=main
[buildstatus-url]: https://github.com/Spill-Tea/PyTemplate/actions?query=branch%3Amain

Python Project Template. Be sure to create a template directly
from github.

<!-- omit in toc -->
## Table of Contents
- [PyTemplate](#pytemplate)
  - [Using this template](#using-this-template)
    - [Manual Editing of Project Template](#manual-editing-of-project-template)
  - [Installation](#installation)
  - [For Developers](#for-developers)
  - [License](#license)

## Using this template
Create a new repository using the `Use this template` option available on github.
Clone that new repository (e.g. `mynewproject`), and run the helper script `rename.py`.

```bash
git clone https://github.com/<username>/<projectname>.git
cd <projectname>
python rename.py --old-name PyTemplate --new-name <projectname>

```
We provide a simple helper script `rename.py` in the root directory to help rename a few
files and directory names to make your life easier. Please note that you will still need
to manually adjust the `pyproject.toml` file, specifically the `[project]` and
`[project.urls]` keys, to reflect your new project metadata.

Also manually update the `docs/source/conf.py` file to reflect correct `author`,
`copyright`, and `release` key metadata for documentation builds.

Finally update this `README.md` document to reflect new project urls.

### Manual Editing of Project Template
To summarize, after running the `rename.py` script, there are three files you may need
to manually adjust for your new project:

1. `pyproject.toml` --> update metadata
1. `docs/source/conf.py` --> update metadata
1. `README.md` --> update project urls (and license type if different)

Note: If you need to update the `LICENSE` file, you will also need to edit the license
header from files throughout the `src/` and `tests/` directories.

PRO-TIP: you could theoretically run the helper script several times to replace the
project name, author name, email, and (github) username. Something like:

```bash
python rename.py --old-name PyTemplate --new-name <project_name>
python rename.py --old-name 'Jason C Del Rio' --new-name <author_name>
python rename.py --old-name spillthetea917@gmail.com --new-name <author_email>
python rename.py --old-name Spill-Tea --new-name <github_user_name>
```

## Installation
Clone the repository and pip install.

```bash
git clone https://github.com/Spill-Tea/PyTemplate.git
cd PyTemplate
pip install .
```

Alternatively, you may install directly from github.
```bash
pip install git+https://github.com/Spill-Tea/PyTemplate@main
```


## For Developers
After cloning the repository, create a new virtual environment and run the following
commands:

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

Running unit tests locally is straightforward with tox. Make sure
you have all python versions available required for your project
The `p` flag is not required, but it runs tox environments in parallel.
```bash
tox -p
```
Be sure to run tox before creating a pull request.

## License
[BSD-3](LICENSE)
