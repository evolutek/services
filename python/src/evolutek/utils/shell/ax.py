from evolutek.utils.shell.shell_global import cs, get_robot

import click
from click_shell import make_click_shell

ID = 0
ROBOT = None

def get_prompt():
    return "ax-shell [%s-%d] > " % (get_robot(), ID)

@click.group(invoke_without_command=True)
@click.pass_context
def ax_shell(ctx):
    global ROBOT
    ROBOT = get_robot()
    if ctx.invoked_subcommand is None:
        subshell = make_click_shell(ctx, prompt=get_prompt, intro='Shell to control AX12')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch ax shell')

@ax_shell.command()
@click.argument('id', type=int, required=False)
def id(id):
    global ID

    if id is None:
        click.echo('Current id: %s' % str(ID))
    else :
        if id < 0 or id > 255:
            click.echo('Bad id [%d]' % id)
            return

        click.echo('Setting id [%d]' % id)
        ID = id

@ax_shell.command()
def status():
    ax = cs.ax['%s-%d' % (ROBOT, ID)]
    click.echo("AX:          {:4}".format(ax.identification))
    click.echo("Position:    {:4}".format(ax.get_present_position()))
    click.echo("Voltage:     {:4}".format(ax.get_present_voltage()))
    click.echo("Temperature: {:4}".format(ax.get_present_temperature()))
    click.echo("Load:        {:4}".format(ax.get_present_load()))

@ax_shell.command()
def reset():
    click.echo('Reset ax [%d]' % ID)
    cs.ax['%s-%s' % (ROBOT, ID)].reset()

@ax_shell.command()
@click.argument('goal', type=int)
def move(goal):
    if goal < 0 or goal > 1023:
        click.echo('Bad goal %d' % goal)
        return

    click.echo('Moving ax [%s-%d] to %d' % (ROBOT, ID, goal))
    cs.ax['%s-%d' % (ROBOT, ID)].mode_joint()
    cs.ax['%s-%d' % (ROBOT, ID)].move(goal=goal)

@ax_shell.command()
@click.argument('side', type=bool)
@click.argument('speed', type=int)
def speed(side, speed):
    if speed < 0 or speed > 1023:
        click.echo('Bad speed %d' % speed)
        return

    click.echo('Setting ax [%d] to %d speed' % (ID, speed))
    cs.ax['%s-%d' % (ROBOT, ID)].mode_wheel()
    cs.ax['%s-%d' % (get_robot(), ID)].turn(side=side, speed=speed)

@ax_shell.command()
def stop():
    click.echo('Stopping ax [%d]' % speed)
    cs.ax['%s-%d' % (ROBOT, ID)].moving_speed(0)
