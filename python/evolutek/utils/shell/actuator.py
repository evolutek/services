from evolutek.utils.shell.shell_global import cs, get_robot
#from evolutek.services.actuators import Actuators
import click
from click_shell import make_click_shell
from click_shell import shell

ROBOT = None

def get_prompt():
    return "act-shell [%s] > " % get_robot()


@click.group(invoke_without_command=True)
@click.pass_context
def actuator_shell(ctx):
    if ctx.invoked_subcommand is None:
        global ROBOT
        ROBOT = get_robot()
        subshell = make_click_shell(
            ctx, prompt=get_prompt, intro='Shell to control actuator')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch actuator shell')

@actuator_shell.command()
def reset():
    cs.actuators[ROBOT].reset()
    return

@actuator_shell.command()
def free():
    cs.actuators[ROBOT].free()
    return


@actuator_shell.command()
def disable():
    cs.actuators[ROBOT].disable()
    return

@actuator_shell.command()
def enable():
    cs.actuators[ROBOT].enable()
    return

@actuator_shell.command()
def start():
    cs.actuators[ROBOT].start()
    return

@actuator_shell.command()
def stop():
    cs.actuators[ROBOT].stop()
    return

@actuator_shell.command()
def print_status():
    cs.actuators[ROBOT].print_status()
    return

@actuator_shell.command()
def get_status():
    cs.actuators[ROBOT].get_status()
    return

@actuator_shell.command()
def flags_raise():
    cs.actuators[ROBOT].flags_raise()
    return

@actuator_shell.command()
def flags_low():
    cs.actuators[ROBOT].flags_low()
    return

@actuator_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_get(pump, buoy='unknow'):
    cs.actuators[ROBOT].pump_get(pump, buoy)
    return

@actuator_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_set(pump, buoy='unknow'):
    cs.actuators[ROBOT].pump_set(pump, buoy)
    return

@actuator_shell.command()
@click.argument('pump', required=True, type=int)
def pump_drop(pump):
    cs.actuators[ROBOT].pump_drop(pump)
    return

@actuator_shell.command()
@click.argument('sensor')
def rgb_sensor_read(sensor):
    if int(sensor) != 1 and int(sensor) != 2:
        print('[ACTUATOR] TRY TO READ A NOT VALID SENSOR [{}]'.format(sensor))
    cs.actuators[ROBOT].rgb_sensor_read(sensor)
    return

@actuator_shell.command()
def left_arm_close():
    cs.actuators[ROBOT].left_arm_close()
    return

@actuator_shell.command()
def left_arm_open():
    cs.actuators[ROBOT].left_arm_open()
    return

@actuator_shell.command()
def right_arm_close():
    cs.actuators[ROBOT].right_arm_close()
    return

@actuator_shell.command()
def right_arm_open():
    cs.actuators[ROBOT].right_arm_open()
    return

@actuator_shell.command()
def left_cup_holder_close():
    cs.actuators[ROBOT].left_cup_holder_close()
    return

@actuator_shell.command()
def left_cup_holder_open():
    cs.actuators[ROBOT].left_cup_holder_open()
    return

@actuator_shell.command()
def right_cup_holder_close():
    cs.actuators[ROBOT].right_cup_holder_close()
    return

@actuator_shell.command()
def right_cup_holder_open():
    cs.actuators[ROBOT].right_cup_holder_open()
    return

@actuator_shell.command()
def _windsocks_push():
    cs.actuators[ROBOT]._windsocks_push()
    return

@actuator_shell.command()
def windsocks_push():
    cs.actuators[ROBOT].windsocks_push()
    return
