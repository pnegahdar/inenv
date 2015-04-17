# InEnv #

A simple utility to manage multiple virtual python environments in one project. Functionally similar to tox but makes no assumption what you want to use it for (tests, etc).

Changes are automatically detected in files and deps and are only reinstalled if changes occur

### Install ###

    pip install inenv

### Usage ###

Basic usage:

    inenv run <envname> <any subprocess command>
    inenv clean <project>

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
