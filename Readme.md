# InEnv #

A simple utility to manage multiple virtual python environments and activate them when you need it 


### Install ###

    pip install inenv

### Usage ###


Example Usage:

    # Switches your current env to webproject
    inenv webproject 

    # Runs `python manage.py syncdb` in the webproject venv
    # Use posix style -- to pass all args
    inenv webproject -- python manage.py syncdb --hello 


Helps Docs:

    Basic usage:
    
    Usage:
    1. inenv ENV_NAME OPTIONS
    Switches to venv ENV_NAME.
    
    2. inenv ENV_NAME OPTIONS -- COMMANDS
    Runs commands in the specified venv.
    Alternatively, you can run: inenv run ENV_NAME OPTIONS -- COMMANDS

    3. inenv runall OPTIONS -- COMMANDS
    Runs commands in all existing venvs.
    
    4. inenv SUB_COMMAND ARGS OPTIONS
    See list of sub-commands.
    
    Options:
      --help, -h: Print the help message and exit
      --quiet, -q: Does not print anything to stdout.
      --verbose, -v: Prints output of installations
      --nobuild, -n: Does not install packages
    
    Sub-commands:
      init ENV_NAME_1 ENV_NAME_2 Etc.:
           Initializes all listed venvs.
           If no venvs are listed, it initializes all of them.
    
      clean ENV_NAME_1 ENV_NAME_2 Etc.:
           Deletes the listed venvs to start over.





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
