# InEnv #

A simple utility to manage multiple virtual python environments in one project. Functionally similar to tox but makes no assumption what you want to use it for (tests, etc).


### Install ###

    pip install inenv

### Usage ###

Basic usage:

    Usage: inenv [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      clean  Deletes the given venv to start over
      init   Sets up all the venvs for the project
      irun   Runs a command in the env provided without prep (pip installs)
      run    Runs a command in the env provided with prep (pip installs)

Example Usage:

    inenv run webproject python manage.py syncdb

    inenv run subproject nosetest

    inenv run webproject -- python manage.py syncdb --hello # Use posix style -- to pass all args




### Config File ###

Config format:

    [envname:<env_var_conditional>]
    deps: (file:)<deplist>, more deps...



Sample config:

    [app1]
    deps: scipy==1.2.1, file:requirements.txt # Relative paths are from the position of the ini file

    [app1:jenkins] # Only used in bool(os.getenv('jenkins')) == True
    deps: scipy==1.4

    [app2]
    deps: file:my/sub/dir/requirements.txt



### Setup/Deveop ###

Clone repo, run `make setup`, test with `make test`
