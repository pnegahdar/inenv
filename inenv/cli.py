import copy
import sys
import shutil
import os

import click

from inenv import InenvManager, INENV_ENV_VAR, EVAL_EXIT_CODE, InenvException
import version


def activator_warn(inenv):
    click.echo(click.style("Please add the following to your bash RC for auto switch.", fg='red'))
    click.echo(click.style("source {file}".format(file=inenv.activate_file), fg='green'))


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx)
                   if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail('Too many matches: %s' % ', '.join(sorted(matches)))


@click.group(cls=AliasedGroup)
def main_cli():
    pass


def _run(venv_name, cmd):
    if len(cmd) == 1:
        cmd = cmd[0].split()
    inenv = InenvManager()
    venv = inenv.get_prepped_venv(venv_name)
    venv.run(cmd, exit=True)


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
def clean(venv_name):
    inenv = InenvManager()
    venv = inenv.get_venv(venv_name)
    click.confirm("Delete dir {}".format(venv.path))
    shutil.rmtree(venv.path)


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


@main_cli.command()
@click.argument('cmd', nargs=-1)
# Backwards compatibility
def should_eval(cmd):
    InenvManager()
    click.echo(click.style("Inenv has been upgrade please start a new shell session.", fg='red'))


@main_cli.command('version')
def print_version():
    print version.__version__


def run_cli():
    try:
        inenv = InenvManager(no_setup=True)
        for venv in inenv.registered_venvs.keys():
            new_switch = copy.deepcopy(switch_or_run)
            for param in new_switch.params:
                if param.name == 'venv_name':
                    param.default = venv
            main_cli.add_command(new_switch, name=venv)
    except InenvException as e:
        pass
    try:
        main_cli(obj={})
    except InenvException as e:
        click.echo(click.style("{}".format(e.message), fg='red'))


if __name__ == '__main__':
    run_cli()


