import copy
import shutil
import os
import sys

import click

from inenv import (InenvManager, INENV_ENV_VAR, EVAL_EXIT_CODE, InenvException,
                   autojump_enabled, toggle_autojump)
from utils import override_envars_and_deactivate
import version


def activator_warn(inenv):
    click.echo(click.style("Please add the following to your bash RC for auto switch.", fg='red'))
    click.echo(click.style("source {file}".format(file=inenv.activate_file), fg='green'))


class InenvCliGroup(click.Group):
    sort_later = set()

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

    def add_command(self, cmd, name=None, sort_later=False):
        super(InenvCliGroup, self).add_command(cmd, name=name)
        if sort_later:
            self.sort_later.add(name)

    def list_commands(self, ctx):
        core_commands, sort_later_commands = [], []
        for k, v in self.commands.items():
            if k in self.sort_later:
                sort_later_commands.append(k)
            else:
                core_commands.append(k)
        return sorted(core_commands) + sorted(sort_later_commands)

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        core_commands, inenv_commands = [], []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue

            help = cmd.short_help or ''
            if subcommand in self.sort_later:
                inenv_commands.append((subcommand, help))
            else:
                core_commands.append((subcommand, help))

        if core_commands:
            with formatter.section('Commands'):
                formatter.write_dl(core_commands)

        if inenv_commands:
            with formatter.section('Inenvs'):
                formatter.write_dl(inenv_commands)


@click.group(cls=InenvCliGroup, name='inenv')
@click.version_option(version=version.__version__)
def main_cli():
    pass


def _run(venv_name, cmd):
    if len(cmd) == 1:
        cmd = cmd[0].split()
    inenv = InenvManager()
    venv = inenv.get_prepped_venv(venv_name)
    venv.run(cmd, always_exit=True)


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
        inenv.write_extra_source_file(override_envars_and_deactivate(inenv.get_envvars(venv_name)))
        if autojump_enabled():
            dir = inenv.guess_contents_dir(venv_name)
            inenv.write_extra_source_file('cd {}'.format(dir))
            click.echo(click.style("Jumping to {}".format(dir), fg='green'))
        sys.exit(EVAL_EXIT_CODE)


@click.argument('venv_name')
@main_cli.command()
def rm(venv_name):
    """ Removes the venv by name """
    inenv = InenvManager()
    venv = inenv.get_venv(venv_name)
    click.confirm("Delete dir {}".format(venv.path))
    shutil.rmtree(venv.path)


@click.argument('venv_name')
@main_cli.command()
def root(venv_name):
    """ Removes the venv by name """
    inenv = InenvManager()
    inenv.get_venv(venv_name)
    venv = inenv.registered_venvs[venv_name]
    click.echo(venv['root'])


@click.argument('venv_name')
@main_cli.command()
def init(venv_name):
    """Initializez a virtualenv"""
    inenv = InenvManager()
    inenv.get_prepped_venv(venv_name, skip_cached=False)
    if not os.getenv(INENV_ENV_VAR):
        activator_warn(inenv)
    click.echo(click.style("Your venv is ready. Enjoy!", fg='green'))


@main_cli.command()
def autojump():
    """Initializes a virtualenv"""
    currently_enabled = autojump_enabled()
    toggle_autojump()
    if not currently_enabled:
        click.echo(click.style("Autojump enabled", fg='green'))
    else:
        click.echo(click.style("Autojump disabled", fg='red'))


@main_cli.command()
def extra_source():
    """Path to file sourced after an inenv switch"""
    inenv = InenvManager()
    print inenv.extra_source_file


@main_cli.command('version')
def print_version():
    """Print the inenv version"""
    print version.__version__


def run_cli():
    try:
        inenv = InenvManager()
        for venv in inenv.registered_venvs.keys():
            new_switch = copy.deepcopy(switch_or_run)
            for param in new_switch.params:
                if param.name == 'venv_name':
                    param.default = venv
            main_cli.add_command(new_switch, name=venv, sort_later=True)
        main_cli(obj={}, prog_name="inenv")
    except InenvException as e:
        click.echo(click.style("{}".format(e.message), fg='red'))


if __name__ == '__main__':
    run_cli()
