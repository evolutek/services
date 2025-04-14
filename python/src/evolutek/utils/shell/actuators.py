from evolutek.utils.shell.shell_global import cs, get_robot
import click
from click_shell import make_click_shell
from click_shell import shell

ROBOT = None

def get_prompt():
    return "act-shell [%s] > " % get_robot()


@click.group(invoke_without_command=True)
@click.pass_context
def actuators_shell(ctx):
    if ctx.invoked_subcommand is None:
        global ROBOT
        ROBOT = get_robot()
        subshell = make_click_shell(
            ctx, prompt=get_prompt, intro='Shell to control actuators')
        subshell.cmdloop()
    else:
        click.echo('[SHELL] Failed to launch actuators shell')

@actuators_shell.command()
def reset():
    cs.actuators[ROBOT].reset()
    return

@actuators_shell.command()
def free():
    cs.actuators[ROBOT].free()
    return


@actuators_shell.command()
def disable():
    cs.actuators[ROBOT].disable()
    return

@actuators_shell.command()
def enable():
    cs.actuators[ROBOT].enable()
    return

@actuators_shell.command()
def start():
    cs.actuators[ROBOT].start()
    return

@actuators_shell.command()
def stop():
    cs.actuators[ROBOT].stop()
    return

@actuators_shell.command()
def print_status():
    cs.actuators[ROBOT].print_status()
    return

@actuators_shell.command()
def get_status():
    cs.actuators[ROBOT].get_status()
    return

@actuators_shell.command()
def flags_raise():
    cs.actuators[ROBOT].flags_raise()
    return

@actuators_shell.command()
def flags_low():
    cs.actuators[ROBOT].flags_low()
    return

@actuators_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_get(pump, buoy='unknown'):
    cs.actuators[ROBOT].pump_get(pump, buoy if buoy is not None else 'unknown')
    return

@actuators_shell.command()
@click.argument('pump', required=True, type=int)
@click.argument('buoy', required=False)
def pump_set(pump, buoy='unknown'):
    cs.actuators[ROBOT].pump_set(pump, buoy if buoy is not None else 'unknown')
    return

@actuators_shell.command()
@click.argument('pump', required=True, type=int)
def pump_drop(pump):
    cs.actuators[ROBOT].pump_drop(pump)
    return

@actuators_shell.command()
@click.argument('sensor')
def rgb_sensor_read(sensor):
    if sensor != "1" and sensor != "2":
        print('[ACTUATOR] TRY TO READ A NOT VALID SENSOR')
    print(cs.actuators[ROBOT].rgb_sensor_read(sensor))
    return

@actuators_shell.command()
def left_arm_close():
    cs.actuators[ROBOT].left_arm_close()
    return

@actuators_shell.command()
def left_arm_open():
    cs.actuators[ROBOT].left_arm_open()
    return

@actuators_shell.command()
def right_arm_close():
    cs.actuators[ROBOT].right_arm_close()
    return

@actuators_shell.command()
def right_arm_open():
    cs.actuators[ROBOT].right_arm_open()
    return

@actuators_shell.command()
def left_cup_holder_close():
    cs.actuators[ROBOT].left_cup_holder_close()
    return

@actuators_shell.command()
def left_cup_holder_open():
    cs.actuators[ROBOT].left_cup_holder_open()
    return

@actuators_shell.command()
def right_cup_holder_close():
    cs.actuators[ROBOT].right_cup_holder_close()
    return

@actuators_shell.command()
def right_cup_holder_open():
    cs.actuators[ROBOT].right_cup_holder_open()
    return

# High level actions

@actuators_shell.command()
def start_lighthouse():
    cs.actuators[ROBOT].start_lighthouse()
    return

@actuators_shell.command()
def drop_starting_without_sort():
    cs.actuators[ROBOT].drop_starting_without_sort()
    return

@actuators_shell.command()
def drop_starting_with_sort():
    cs.actuators[ROBOT].drop_starting_with_sort()
    return

@actuators_shell.command()
def drop_center_zone():
    cs.actuators[ROBOT].drop_center_zone()
    return

@actuators_shell.command()
def get_reef_buoys():
    cs.actuators[ROBOT].get_reef_buoys()
    return

@actuators_shell.command()
def windsocks_push():
    cs.actuators[ROBOT].windsocks_push()
    return

@actuators_shell.command()
def get_pattern():
    cs.actuators[ROBOT].get_pattern()
    return

@actuators_shell.command()
def get_reef():
    cs.actuators[ROBOT].get_reef()
    return

@actuators_shell.command()
def go_to_anchorage():
    cs.actuators[ROBOT].go_to_anchorage()
    return
