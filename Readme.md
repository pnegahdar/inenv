# InEnv #

A simple utility to manage multiple virtual python environments in one project. Functionally similar to tox but makes no assumption what you want to use it for (tests, etc).

Changes are automatically detected in files and deps and are only reinstalled if changes occur

### Usage ###

Basic usage:

    inenv run <envname> <any subprocess command>
    inenv clean <project>

Example Usage:

    inenv run webproject python manage.py syncdb

    inenv run subproject nosetest




### Config File ###

Config format:

    [envname:<env_var_conditional>]
    env_storage: /workspace/ # Path to store the venv, defaults to .inenv/ where the ini is.
    deps: (file:)<deplist>, more deps...



Sample config:

    [app1]
    deps: scipy==1.2.1, file:requirements.txt # Relative paths are from the position of the ini file

    [app1:jenkins] # Only used in bool(os.getenv('jenkins')) == True
    env_storage: ~/workspace/

    [app2]
    deps: file:my/sub/dir/requirements.txt



### Setup/Deveop ###

Clone repo, run `make setup`, test with `make test`
