from shell_global import cs

import click
from click_shell import make_click_shell

@click.group(invoke_without_command=True)
@click.pass_context
def config_shell(ctx):
    if ctx.invoked_subcommand is None:
        subshell = make_click_shell(ctx, prompt='config-shell > ', intro='Shell to control Config')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch config shell')

@config_shell.command()
@click.argument('section')
@click.option('--option', default=None, help='specific option in section')
def get(section, option):
    if option is None:
        click.echo(cs.config.get_section(name=section))
    else:
        click.echo(cs.config.get(section=section, option=option))

@config_shell.command()
@click.argument('section')
@click.argument('option')
@click.argument('value')
@click.option('-t', '--tmp/--no-tmp', default=False, help='if value will be tmp')
def set(section, option, value, tmp):
    click.echo('Setting config')
    if tmp:
        cs.config.set_tmp(section=section, option=option, value=value)
    else:
        cs.config.set(section=section, option=option, value=value)

@config_shell.command()
def list():
    click.echo(cs.config.list())

@config_shell.command()
def write():
    click.echo('Writing config file')
    cs.config.write()
