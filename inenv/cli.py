import copy
import sys
import os

import click

from inenv import InenvManager, INENV_ENV_VAR, EVAL_EXIT_CODE, InenvException


def activator_warn(inenv):
    click.echo(click.style("Please add the following to your bash RC for auto switch.", fg='red'))
    click.echo(click.style("source {file}".format(file=inenv.activate_file), fg='green'))


@click.group()
def main_cli():
    pass


def _run(venv_name, cmd):
    if len(cmd) == 1:
        cmd = cmd[0].split()
    inenv = InenvManager()
    venv = inenv.get_prepped_venv(venv_name)
    venv.run(cmd, exit=True)


@click.argument('cmd', nargs=-1)
@main_cli.command()
def run(venv_name, cmd):
    """Runs command in venv"""
    _run(venv_name, cmd)


@click.argument('cmd', nargs=-1)
@click.option('--venv_name', default=None)
@click.command()
def switch_or_run(cmd, venv_name=None):
    """Switch or run in this env"""
    if cmd:
        return _run(venv_name, cmd)
    inenv = InenvManager()
    if not os.getenv(INENV_ENV_VAR):
        activator_warn(inenv)
        return
    else:
        venv = inenv.get_prepped_venv(venv_name)
        inenv.clear_extra_source_file()
        inenv.write_extra_source_file("source {}".format(venv.activate_shell_file))
        sys.exit(EVAL_EXIT_CODE)


@click.argument('venv_name')
@main_cli.command()
def init(venv_name):
    """Initializez a virtualenv"""
    inenv = InenvManager()
    inenv.get_prepped_venv(venv_name)
    activator_warn(inenv)


@main_cli.command()
def extra_source():
    inenv = InenvManager()
    print inenv.extra_source_file


def run_cli():
    try:
        inenv = InenvManager()
        for venv in inenv.registered_venvs.keys():
            new_switch = copy.deepcopy(switch_or_run)
            for param in new_switch.params:
                if param.name == 'venv_name':
                    param.default = venv
            main_cli.add_command(new_switch, name=venv)
        main_cli(obj={})
    except InenvException as e:
        click.echo(click.style("{}".format(e.message), fg='red'))


if __name__ == '__main__':
    run_cli()


