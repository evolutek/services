from evolutek.utils.shell.shell_global import cs, get_robot
from evolutek.services.actuators import Actuators
import click
from click_shell import make_click_shell
from click_shell import shell

ACT = Actuators()
ROBOT = None

def get_prompt():
    return "evo-shell [%s] > " % get_robot()


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
    ACT.reset()
    return

@actuator_shell.command()
def free():
    ACT.free()
    return


@actuator_shell.command()
def disable():
    ACT.disable()
    return

@actuator_shell.command()
def enable():
    ACT.enable()
    return

@actuator_shell.command()
def start():
    ACT.start()
    return

@actuator_shell.command()
def stop():
    ACT.stop()
    return

@actuator_shell.command()
def print_status():
    ACT.print_status()
    return

@actuator_shell.command()
def get_status():
    ACT.get_status()
    return

@actuator_shell.command()
def flags_raise():
    ACT.free()
    return

@actuator_shell.command()
def flags_low():
    ACT.free()
    return

@actuator_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_get(pump, buoy='unknow'):
    ACT.pump_get(pump, buoy)
    return

@actuator_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_set(pump, buoy='unknow'):
    ACT.pump_set(pump, buoy)
    return

@actuator_shell.command()
def pump_drop():
    ACT.pump_drop()
    return

@actuator_shell.command()
@click.argument('sensor')
def rgb_sensor_read(sensor):
    if sensor != 1 and sensor != 2:
        print('[ACTUATOR] TRY TO READ A NOT VALID SENSOR')
    ACT.rgb_sensor_read()
    return

@actuactor_shell.command()
def left_arm_close():
    global ROBOT
    if ROBOT is None:
        print('[ACTUATOR] ROBOT NOT SET...')
        return
    ACT.left_arm_close()
    return

@actuactor_shell.command()
def left_arm_open():
    ACT.left_arm_open()
    return

@actuactor_shell.command()
def right_arm_close():
    ACT.right_arm_close()
    return

@actuactor_shell.command()
def right_arm_open():
    ACT.right_arm_open()
    return

@actuactor_shell.command()
def left_cup_holder_close():
    ACT.left_cup_holder_close()
    return

@actuactor_shell.command()
def left_cup_holder_open():
    ACT.left_cup_holder_open()
    return

@actuactor_shell.command()
def right_cup_holder_close():
    ACT.right_cup_holder_close()
    return

@actuactor_shell.command()
def right_cup_holder_open():
    ACT.right_cup_holder_open()
    return

@actuactor_shell.command()
def _windsocks_push():
    ACT._windsocks_push()
    return

@actuactor_shell.command()
def windsocks_push():
    ACT.windsocks_push()
    return
