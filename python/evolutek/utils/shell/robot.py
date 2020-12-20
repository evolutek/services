from evolutek.lib.robot import Robot

from evolutek.utils.shell.shell_global import cs, get_robot
from evolutek.utils.shell.data_printer import print_json

import click
from click_shell import make_click_shell

ROBOT = None
robot = None

#TODO: Display move status
#TODO: Manage avoid moves

def get_prompt():
    return "robot-shell [%s] > " % ROBOT

@click.group(invoke_without_command=True)
@click.pass_context
def robot_shell(ctx):
    if ctx.invoked_subcommand is None:
        global ROBOT
        ROBOT = get_robot()
        global robot
        robot = Robot(ROBOT)
        subshell = make_click_shell(ctx, prompt=get_prompt, intro='Shell to control Robot')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch trajman shell')

@robot_shell.command()
def free():
    click.echo('Freeing robot [%s]' % ROBOT)
    robot.tm.free()

@robot_shell.command()
def unfree():
    click.echo('Unfreeing robot [%s]' % ROBOT)
    robot.tm.unfree()

@robot_shell.command()
def disable():
    click.echo('Disabling robot [%s]' % ROBOT)
    robot.tm.disable()

@robot_shell.command()
def enable():
    click.echo('Enabling robot [%s]' % ROBOT)
    robot.tm.enable()

""" MOVE """
@robot_shell.command()
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.option('-b', '--block/--no-block', default=False, help='Makes the operation blocking (not async)')
@click.option('-m', '--mirror/--no-mirror', default=False, help='Mirrors the position of the robot')
@click.option('-a', '--avoid/--no-avoid', default=False, help='Makes the robot use avoid')
@click.option('-p', '--pathfinding/--no-pathfinding', default=False, help='Makes the robot use the pathfinding')
def goto(x, y, block, mirror, avoid, pathfinding):
    click.echo('Going to %f %f with robot[%s]' % (x, y, ROBOT))
    if pathfinding:
        robot.goto_with_path(x=x, y=y, mirror=mirror)
    elif avoid:
        robot.goto_avoid(x=x, y=y, mirror=mirror)
    elif block:
        robot.goto(x=x, y=y, mirror=mirror)
    else:
        if mirror:
            y = 1500 + (1500 - y) * (-1 if not self.side else 1)
        robot.tm.goto_xy(x=x, y=y)

@robot_shell.command()
@click.argument('theta', type=float)
@click.option('-b', '--block/--no-block', default=False, help='if call will be blocking')
@click.option('-m', '--mirror/--no-mirror', default=False, help='if pos will be mirror')
def goth(theta, block, mirror):
    click.echo('Going to %f with robot[%s]' % (theta, ROBOT))
    if block:
        robot.goth(theta=theta, mirror=mirror)
    else:
        if mirror:
            th = th * (1 if not self.side else -1)
        robot.tm.goto_theta(theta=theta)

@robot_shell.command()
@click.argument('dest', type=float)
@click.argument('acc', type=float)
@click.argument('dec', type=float)
@click.argument('maxspeed', type=float)
@click.argument('sens', type=bool)
@click.option('-b', '--block/--no-block', default=False, help='if call will be blocking')
def move_trsl(dest, acc, dec, maxspeed, sens, block):
    click.echo('Moving trsl of %f with robot[%s]' % (dest, ROBOT))
    if block:
        robot.move_trsl_block(dest, acc, dec, maxspeed, sens)
    else:
        robot.tm.move_trsl(dest, acc, dec, maxspeed, sens)

@robot_shell.command()
@click.argument('dest', type=float)
@click.argument('acc', type=float)
@click.argument('dec', type=float)
@click.argument('maxspeed', type=float)
@click.argument('sens', type=bool)
@click.option('-b', '--block/--no-block', default=False, help='if call will be blocking')
def move_rot(dest, acc, dec, maxspeed, sens, block):
    click.echo('Moving rot of %f with robot[%s]' % (dest, ROBOT))
    if block:
        robot.move_rot_block(dest, acc, dec, maxspeed, sens)
    else:
        robot.tm.move_rot(dest, acc, dec, maxspeed, sens)

@robot_shell.command()
@click.argument('sens', type=bool)
@click.option('-d', '--decal', default=0.0, help='tell the decalage')
@click.option('-n', '--no-set/--set', default=False, help='disable the postion setting')
@click.option('-b', '--block/--no-block', default=False, help='if call will be blocking')
def recalibration(sens, decal, no_set, block):
    if block:
        robot.recalibration_block(sens=sens, decal=decal_x, set=not no_set)
    else:
        robot.tm.recalibration(sens=sens, decal=decal_x, set=not no_set)

@robot_shell.command()
@click.argument('trsldec', type=float)
@click.argument('rotdec', type=float)
def stop_asap(trsldec, rotdec):
    click.echo('Stopping robot [%s]' % ROBOT)
    robot.tm.stop_asap(trsldec, rotdec)

""" SET """
@robot_shell.command()
@click.argument('enable', type=bool)
def debug(enable):
    """Set the debug state."""
    robot.tm.set_debug(enable)

@robot_shell.command()
@click.argument('x', type=float)
def set_x(x):
    click.echo('Setting robot [%s] to x=%f' % (ROBOT, x))
    robot.set_x(x)

@robot_shell.command()
@click.argument('y', type=float)
@click.option('-m', '--mirror/--no-mirror', default=False, help='if pos will be mirror')
def set_y(y, mirror):
    click.echo('Setting robot [%s] to y=%f' % (ROBOT, y))
    robot.set_y(y, mirror=mirror)

@robot_shell.command()
@click.argument('theta', type=float)
@click.option('-m', '--mirror/--no-mirror', default=False, help='if pos will be mirror')
def set_theta(theta, mirror):
    click.echo('Setting robot [%s] to theta=%f' % (ROBOT, theta))
    robot.set_theta(theta, mirror=mirror)

@robot_shell.command()
@click.argument('x', type=float)
@click.argument('y', type=float)
@click.argument('theta', type=float)
@click.option('-m', '--mirror/--no-mirror', default=False, help='if pos will be mirror')
def set_pos(x, y, theta, mirror):
    click.echo('Setting robot [%s] to x=%f, y=%f, theta=%f' % (ROBOT, x, y, theta))
    robot.set_pos(x=x, y=y, theta=theta, mirror=mirror)

@robot_shell.command()
@click.argument('acc', type=float)
def set_trsl_acc(acc):
    click.echo('Setting trsl_acc=%s of robot [%s]' % (acc, ROBOT))
    robot.tm.set_trsl_acc(acc=acc)

@robot_shell.command()
@click.argument('maxspeed', type=float)
def set_trsl_max_speed(maxspeed):
    click.echo('Setting trsl_maxspeed=%s of robot [%s]' % (maxspeed, ROBOT))
    robot.tm.set_trsl_max_speed(maxspeed=maxspeed)

@robot_shell.command()
@click.argument('dec', type=float)
def set_trsl_dec(dec):
    click.echo('Setting trsl_dec=%s of robot [%s]' % (dec, ROBOT))
    robot.tm.set_trsl_dec(dec=dec)

@robot_shell.command()
@click.argument('acc', type=float)
def set_rot_acc(acc):
    click.echo('Setting rot_acc=%s of robot [%s]' % (acc, ROBOT))
    robot.tm.set_rot_acc(acc=acc)

@robot_shell.command()
@click.argument('maxspeed', type=float)
def set_rot_max_speed(maxspeed):
    click.echo('Setting rot_speed=%s of robot [%s]' % (maxspeed, ROBOT))
    robot.tm.set_rot_max_speed(maxspeed=maxspeed)

@robot_shell.command()
@click.argument('dec', type=float)
def set_rot_dec(dec):
    click.echo('Setting rot_dec=%s of robot [%s]' % (dec, ROBOT))
    robot.tm.set_rot_dec(dec=dec)

""" GET """
@robot_shell.command()
def get_pos():
    print_json(robot.tm.get_position())

@robot_shell.command()
def get_speeds():
    print_json(robot.tm.get_speeds())

@robot_shell.command()
def get_wheels():
    print_json(robot.tm.get_wheels())
