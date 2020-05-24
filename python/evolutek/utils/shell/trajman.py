from shell_global import cs, get_robot
from data_printer import print_json

import click
from click_shell import make_click_shell

ROBOT = None

def get_prompt():
    return "evo-shell [%s] > " % ROBOT

@click.group(invoke_without_command=True)
@click.pass_context
def trajman_shell(ctx):
    if ctx.invoked_subcommand is None:
        global ROBOT
        ROBOT = get_robot()
        subshell = make_click_shell(ctx, prompt=get_prompt, intro='Shell to control Trajman')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch trajman shell')

@trajman_shell.command()
def free():
    click.echo('Freeing robot [%s]' % ROBOT)
    cs.trajman[ROBOT].free()

@trajman_shell.command()
def unfree():
    click.echo('Unfreeing robot [%s]' % ROBOT)
    cs.trajman[ROBOT].unfree()

@trajman_shell.command()
def disable():
    click.echo('Disabling robot [%s]' % ROBOT)
    cs.trajman[ROBOT].disable()

@trajman_shell.command()
def enable():
    click.echo('Enabling robot [%s]' % ROBOT)
    cs.trajman[ROBOT].enable()

""" MOVE """
@trajman_shell.command()
@click.argument('x', type=float)
@click.argument('y', type=float)
def goto_xy(x, y):
    click.echo('Going to %f %f with robot[%s]' % (x, y, ROBOT))
    cs.trajman[ROBOT].goto_xy(x=x, y=y)

@trajman_shell.command()
@click.argument('theta', type=float)
def goto_theta(theta):
    click.echo('Going to %f with robot[%s]' % (theta, ROBOT))
    cs.trajman[ROBOT].goto_theta(theta=theta)

@trajman_shell.command()
@click.argument('dest', type=float)
@click.argument('acc', type=float)
@click.argument('dec', type=float)
@click.argument('maxspeed', type=float)
@click.argument('sens', type=bool)
def move_trsl(dest, acc, dec, maxspeed, sens):
    click.echo('Moving trsl of %f with robot[%s]' % (dest, ROBOT))
    cs.trajman[ROBOT].move_trsl(dest, acc, dec, maxspeed, sens)

@trajman_shell.command()
@click.argument('dest', type=float)
@click.argument('acc', type=float)
@click.argument('dec', type=float)
@click.argument('maxspeed', type=float)
@click.argument('sens', type=bool)
def move_rot(dest, acc, dec, maxspeed, sens):
    click.echo('Moving rot of %f with robot[%s]' % (dest, ROBOT))
    cs.trajman[ROBOT].move_rot(dest, acc, dec, maxspeed, sens)

@trajman_shell.command()
@click.argument('trsldec', type=float)
@click.argument('rotdec', type=float)
def stop_asap(trsldec, rotdec):
    click.echo('Stopping robot [%s]' % ROBOT)
    cs.trajman[ROBOT].stop_asap(trsldec, rotdec)

""" SET """
@trajman_shell.command()
@click.argument('enable', type=bool)
def debug(enable):
    """Set the debug state."""
    cs.trajman[ROBOT].set_debug(enable)

@trajman_shell.command()
@click.argument('x', type=float)
def set_x(x):
    click.echo('Setting robot [%s] to x=%f' % (ROBOT, x))
    cs.trajman[ROBOT].set_x(x)

@trajman_shell.command()
@click.argument('y', type=float)
def set_y(y):
    click.echo('Setting robot [%s] to y=%f' % (ROBOT, y))
    cs.trajman[ROBOT].set_y(y)

@trajman_shell.command()
@click.argument('theta', type=float)
def set_theta(x):
    click.echo('Setting robot [%s] to theta=%f' % (ROBOT, theta))
    cs.trajman[ROBOT].set_tehta(theta)

@trajman_shell.command()
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.argument('theta', type=float)
def set_pos(x, y, theta):
    click.echo('Setting robot [%s] to x=%f, y=%f, theta=%f' % (ROBOT, x, y, theta))

@trajman_shell.command()
@click.argument('acc', type=float)
def set_trsl_acc(acc):
    click.echo('Setting trsl_acc=%s of robot [%s]', (acc, ROBOT))
    cs.trajman[ROBOT].set_trsl_acc(acc=acc)

@trajman_shell.command()
@click.argument('maxspeed', type=float)
def set_trsl_max_speed(maxspeed):
    click.echo('Setting trsl_maxspeed=%s of robot [%s]', (maxspeed, ROBOT))
    cs.trajman[ROBOT].set_trsl_max_speed(maxspeed=maxspeed)

@trajman_shell.command()
@click.argument('dec', type=float)
def set_trsl_dec(dec):
    click.echo('Setting trsl_dec=%s of robot [%s]', (dec, ROBOT))
    cs.trajman[ROBOT].set_trsl_dec(dec=dec)

@trajman_shell.command()
@click.argument('acc', type=float)
def set_rot_acc(acc):
    click.echo('Setting rot_acc=%s of robot [%s]', (acc, ROBOT))
    cs.trajman[ROBOT].set_rot_acc(acc=acc)

@trajman_shell.command()
@click.argument('maxspeed', type=float)
def set_rot_max_speed(maxspeed):
    click.echo('Setting rot_speed=%s of robot [%s]', (maxspeed, ROBOT))
    cs.trajman[ROBOT].set_rot_max_speed(maxspeed=maxspeed)

@trajman_shell.command()
@click.argument('dec', type=float)
def set_rot_dec(dec):
    click.echo('Setting rot_dec=%s of robot [%s]', (dec, ROBOT))
    cs.trajman[ROBOT].set_rot_dec(dec=dec)

""" GET """
@trajman_shell.command()
def get_pos():
    print_json(cs.trajman[ROBOT].get_position())

@trajman_shell.command()
def get_speeds():
    print_json(cs.trajman[ROBOT].get_speeds())

@trajman_shell.command()
def get_wheels():
    print_json(cs.trajman[ROBOT].get_wheels())
