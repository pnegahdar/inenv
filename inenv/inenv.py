# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2015, Parham Negahdar <pnegahdar@gmail.com>
from collections import defaultdict
import ConfigParser
import hashlib
import os
import shutil
import subprocess
import sys

from virtualenv import create_environment
import click

FILE_NAME = 'inenv.ini'

ACTIVATED_VENV = None
INI_PATH = None
RECURSION_LIMIT = 100

### PATH STUFF
def get_ini_path():
    """Walks up till it finds a inenv.ini"""
    global INI_PATH
    directory = os.path.realpath(os.path.curdir)
    if INI_PATH:
        return INI_PATH
    x = RECURSION_LIMIT
    while x > 0:
        ini_path = os.path.join(directory, FILE_NAME)
        if not os.access(directory, os.W_OK):
            exit_with_err(
                "Lost permissions walkign up to {}. Unable to find {}".format(directory, FILE_NAME))
        if os.path.isfile(ini_path):
            INI_PATH = ini_path
            return ini_path
        parent_dir = os.path.realpath(os.path.join(directory, '..'))
        if parent_dir == directory:
            exit_with_err("Walked all the way up to {} and was unable to find {}".format(parent_dir,
                                                                                         FILE_NAME))
        directory = parent_dir
        x -= 1
    exit_with_err("Recursion limit exceeded unable to find inenv.ini")


def get_working_path():
    '''Returns the path which the inenv command was envoked from'''
    return os.path.join(os.path.dirname(get_ini_path()), '.inenv/')


def rel_path_to_abs(path):
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(os.path.dirname(get_ini_path()), path))


def get_venv_path(venv_name):
    return os.path.join(get_working_path(), venv_name)


def get_execfile_path(venv_name):
    return os.path.join(get_venv_path(venv_name), 'bin/activate_this.py')


### Venv Stuff

def subprocess_call(cmd_args):
    proc = subprocess.Popen(' '.join(cmd_args), stdin=sys.stdin, stdout=sys.stdout,
                            stderr=sys.stderr, shell=True)
    retcode = proc.wait()
    if retcode != 0:
        exit_with_err('Runtime Error')


def extract_ini_section(parser, section):
    section_parts = section.split(":")
    data = {}
    try:
        env_name, env_var = section_parts[0], section_parts[1]
    except IndexError:
        env_name, env_var = section_parts[0], None
    if env_var and not os.getenv(env_var):
        return env_name, {}
    data['deps'] = []
    try:
        deps = [dep.strip() for dep in parser.get(section, 'deps').split(',')]
        data['deps'] += deps
    except ConfigParser.NoOptionError:
        pass
    try:
        storage = parser.get(section, 'env_storage')
        if not os.access(os.path.abspath(storage), os.W_OK):
            exit_with_err(
                "INI Parse Error: The env_storage for {} provided is not a directory or doesn't "
                "have write permissions".format(
                    section))
        data['env_stoarge'] = storage
    except ConfigParser.NoOptionError:
        pass
    return env_name, data


def parse_ini(path_to_ini):
    """Should return something like { 'envname' : [deplist] }"""
    parsed = defaultdict(dict)
    parser = ConfigParser.ConfigParser()
    with open(path_to_ini) as parse_file:
        try:
            parser.readfp(parse_file)
        except ConfigParser.ParsingError:
            exit_with_err("Unable to parse your ini file")

    sections = parser.sections()
    for section in sections:
        parsed_section, data = extract_ini_section(parser, section)
        for k, v in data.items():
            parsed[parsed_section][k] = v
    return parsed


def venv_exists(venv_name):
    exec_path = get_execfile_path(venv_name)
    return os.path.isfile(exec_path)


def create_venv(venv_name):
    create_environment(get_venv_path(venv_name))


def delete_venv(venv_name):
    shutil.rmtree(get_venv_path(venv_name))


def file_md5(path):
    """Temporary until pip file parsing is done"""
    hashlib.md5(open(path, 'rb').read()).hexdigest()


def setup_venv(venv_name):
    """Main venv functionality entry point, run before doing things"""
    ini_path = get_ini_path()
    if not venv_exists(venv_name):
        create_venv(venv_name)
    activate_venv(venv_name)
    parsed = parse_ini(ini_path).get(venv_name)
    if not parsed:
        exit_with_err("Unable to find venv {} in ini {}".format(venv_name, ini_path))
    deps = parsed.get('deps', [])
    for dep in deps:
        print "Installing {}".format(dep)
        if dep.startswith('file:'):
            dep = rel_path_to_abs(dep.split('file:')[1])
            subprocess_call(['pip', 'install', '-r', dep])
        else:
            subprocess_call(['pip', 'install', dep])


def activate_venv(venv_name):
    global ACTIVATED_VENV
    if not ACTIVATED_VENV:
        exec_file_path = get_execfile_path(venv_name)
        execfile(exec_file_path, dict(__file__=exec_file_path))
        ACTIVATED_VENV = exec_file_path


def run_in_venv(venv_name, cmd_args):
    setup_venv(venv_name)
    subprocess_call(cmd_args)


def exit_with_err(msg):
    click.echo(click.style(msg, fg='red'), err=True)
    sys.exit(1)


# def sub_shell():
#     shell = os.getenv('SHELL')
#     print shell
#     shell = '/bin/bash'
#     os.execv(shell, ['-l'])
#     # proc = subprocess.Popen(shell, stdin=sys.stdin, stdout=sys.stdout,
#     #                          stderr=sys.stderr, shell=True, executable=shell)
#     # proc.wait()


### CLI
@click.group()
def main_cli():
    pass


@main_cli.command()
@click.argument('venv_name', nargs=1)
@click.argument('cmd', nargs=-1)
def run(venv_name, cmd):
    setup_venv(venv_name)
    run_in_venv(venv_name, cmd)


# @main_cli.command()
# @click.argument('venv_name')
# def switch(venv_name):
#     setup_venv(venv_name)
#     activate_venv(venv_name)
#     sub_shell()

@main_cli.command()
@click.argument('venv_name')
def clean(venv_name):
    venv_path = venv_exists(venv_name)
    if not venv_path:
        exit_with_err('The venv does not exists at {}'.format(get_venv_path(venv_name)))
    run = click.confirm('Going to delete {} venv'.format(venv_name))
    if run:
        delete_venv(venv_name)


if __name__ == '__main__':
    main_cli()

