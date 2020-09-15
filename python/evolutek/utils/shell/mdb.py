from evolutek.lib.robot import Robot
from evolutek.utils.shell.shell_global import cs, get_robot

import click
from click_shell import make_click_shell

ROBOT = None
mdb = None

def get_prompt():
    return "mdb-shell [%s] > " % ROBOT

@click.group(invoke_without_command=True)
@click.pass_context
def mdb_shell(ctx):
    if ctx.invoked_subcommand is None:
        global ROBOT
        global tm
        ROBOT = get_robot()
        tm = Robot(ROBOT).tm
        subshell = make_click_shell(ctx, prompt=get_prompt, intro='Shell to control Mdb')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch mdb shell')

""" CONTROL """

@mdb_shell.command()
def enable():
    click.echo('Enabling MDB')
    tm.enable_mdb()

@mdb_shell.command()
def disable():
    click.echo('Disabling MDB')
    tm.disable_mdb()

@mdb_shell.command()
@click.argument('v', type=bool)
def error_mode(v):
    click.echo(('Enabling' if v else 'Disabling') + ' MDB error mode')
    tm.error_mdb(v)

""" GETTERS """

@mdb_shell.command()
def zones():
    click.echo(str(tm.get_zones()))

@mdb_shell.command()
def scan():
    click.echo(str(tm.get_scan()))

""" SETTERS """

@mdb_shell.command()
@click.argument('v', type=int)
def brightness(v):
    tm.set_mdb_config(brightness=v)

@mdb_shell.command()
@click.argument('v', type=int)
def near(v):
    tm.set_mdb_config(near=v)

@mdb_shell.command()
@click.argument('v', type=int)
def far(v):
    tm.set_mdb_config(far=v)

@mdb_shell.command()
@click.argument('v')
def color(v):
    c = None
    v = v.lower()
    if v in ['yellow', 'y']: c = True
    if v in ['blue', 'b']: c = False
    if c is not None:
        tm.set_mdb_config(yellow=c)
    else: click.echo('Unknown color. Possible values are yellow, blue, y, b')

@mdb_shell.command()
@click.argument('v')
def mode(v):
    v = v.lower()
    if v in ['distances', 'd']: tm.set_mdb_config(mode=0)
    elif v in ['zones', 'z']: tm.set_mdb_config(mode=1)
    elif v in ['loading', 'l']: tm.set_mdb_config(mode=2)
    elif v in ['disabled', 'db']: tm.set_mdb_config(mode=3)
    else: click.echo('Unknown mode. Possible values are distances, zones, loading, disabled, d, z, l, db')
