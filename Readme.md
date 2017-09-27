[![Build Status](https://travis-ci.org/ColCarroll/inenv.svg?branch=master)](https://travis-ci.org/pnegahdar/inenv)
[![Coverage Status](https://coveralls.io/repos/github/pnegahdar/inenv/badge.svg?branch=master)](https://coveralls.io/github/pnegahdar/inenv?branch=master)

Inenv
=======

Inenv is a multi-project virtual enviornment manager, switcher and executor.

### Installation

Install inenv in your global python interpreter (make sure no virtualenvs are activated).

```sh
pip install inenv
```

### Config file

In the root of your project add a file called `inenv.ini`.

```ini
[webproject]
deps: file:requirements.txt

[service]
deps: requests==1.4 file:subproject/app/requirements.txt
root: subproject/app # Optional, used by autojump
env: PYTHONPATH=dir:projects/search/app B=C

[py3app]
deps: aiohttp
python: python3
```

#### Project name

Each project is denoted by `[project_name]`. This venv contents will be in: `/<projects_root>/.inenv/<project_name>`

#### Python

You can specificy which python to use with the python argument. By default it uses your current python.

```ini
python: python3
```

```ini
python: python2
```

#### Deps

A project can have py deps. They can be a file (installed via pip install -r <file>) or a specific dep. They are installed in order separately. File paths are relative to the `inenv.ini`

#### Root

Root is the root of the project. If root is not set it will be the location of the first file dep and if that is not set it is the directory of the `inenv.ini`

#### Env

Key/value pairs that are set in the shell/process that is executed. These revert safely. Values can be prefixed with `dir:` to give the full path from the inenv.ini.

E.x. if /User/me/projects/django_app/inenv.ini `dir:` is the same as `/User/me/projects/django_app/` So setting something like

    env: PYTHONPATH=dir:subdir/app

Would actually set python path to:

    PYTHONPATH= /User/me/projects/django_app/subdir/app

#### Hash

Sometimes you want to force the virtualenv to rebuild on all environments its run on. To do this you can set a hash for the venv:

```ini
hash: rev1
```

Going forward everytime you change the hash the venv will be rebuilt whenever an inenv command is run.

### Useful commands

Execute something in an inenv without modifying current shell:

    inenv <project_name> -- some command


Activating the venv in your current shell:

    inenv <project_name>


To toggle autojump (cd into the `root` of the env after activating the venv):

    inenv autojump

Deactivate the venv in your current shell:

    deactivate


To install all requirements and setup the venv:

    inenv init <project_name>

To remove and clean out all caches/installs:

    inenv rm <project_name>


Get the root of the project venv:

    inenv root <project_name>


View currently activated inenv:

    echo $VIRTUALENV
