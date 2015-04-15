# InEnv #

A simple utility to manage multiple virtual python environments in one project. Functionally similar to tox but makes no assumption assumptions on what you want to use it for (tests, etc).

Changes are automatically detected in files and deps and are only reinstalled if changes occur

### Usage ###

Basic usage:

    inenv run <envname> <any subprocess command>
    inenv recreate <project>

Example Usage:

    inenv run webproject python manage.py syncdb

    inenv run subproject nosetest




### Config File ###

Available params:

    {{ config_dir }} -- the directory of the config
    {{ if:VAR }}something{{ endif }} -- checks if VAR environment variable is set


Config format:

    env_storage: <default {{ config_dir }}/.inenv>
    [envname]
        deps:
            (file:)<deplist>




Sample config:

    {{ if:IS_JENKINS }}
    env_storage: ~/workspace/
    {{ endif }}
    [app1]
        deps:
            scipy==1.2.4
            file:requirements.txt
    [app2]
        deps:
            file:{{ config_dir }}/my/sub/dir/requirements.txt



### Setup/Deveop ###

Clone repo, run `make setup`, test with `make test`
