# author : kapwiing
from cellaserv.proxy import CellaservProxy
from math import pi
from time import sleep

# --HEAD CONFIGS--
# Closed = 0
# Down = 1
# Mid = 2
# Galery = 3

# --ELEVATOR CONFIGS--
# Closed..............0
# Down................1
# Mid.................2
# GaleryLow...........3
# ExcavationSquares...4
# StoreStatuette......5

BotName = "pmi"
default_x = 1550
default_y = 450
default_angle = (5 * pi) / 4

def init_bot():
    """Initialize the bot and return the proxy object"""

    cs: CellaservProxy = CellaservProxy()

    cs.trajman[BotName].free()
    cs.robot[BotName].set_pos(x = default_x, y = default_y, theta = default_angle)
    cs.trajman[BotName].unfree()
    print("\n\nReseting positions...\n\n")
    sleep(1)
    cs.robot[BotName].reset()
    print("Initalization done !")
    return cs

def move_side_arms(status, cs):
    """Move the side arms to the right position
    -head     : move the head of the arms
    -elevator_down : move the elevation of the arms down"""

    print("Moving side arms...")
    if (status == "head"):
        cs.robot[BotName].pumps_get(ids = "1") # Pump the pump 1
        sleep(1)
        cs.robot[BotName].pumps_get(ids = "3") # Pump the pump 3
        sleep(1)
        cs.robot[BotName].set_head_config(arm = 1, config = 1) # Head down
        sleep(1)
        cs.robot[BotName].set_head_config(arm = 3, config = 1) # Head down
    elif (status == "elevator_down"):
        cs.robot[BotName].set_elevator_config(arm = 1, config = 2) # Head mid
        sleep(1)
        cs.robot[BotName].set_elevator_config(arm = 3, config = 2) # Head mid
    elif (status == "elevator_up"):
        cs.robot[BotName].set_elevator_config(arm = 1, config = 0) # Head up
        sleep(1)
        cs.robot[BotName].set_elevator_config(arm = 3, config = 0) # Head up
    else:
        print("Error: wrong status")
        exit(84)
    print(f"Done action : {status}")

def drop_carrying(cs):
    """Drop the carrying statuette"""
    cs.robot[BotName].set_elevator_config(arm = 2, config = 2) # Elevator to mid
    sleep(0.5)
    cs.robot[BotName].set_head_config(arm = 2, config = 0) # Head Closed
    sleep(0.5)
    cs.robot[BotName].pumps_get(ids = "2") # Pump the pump 2
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 5) # Elevator to store statuette
    sleep(0.5)
    cs.robot[BotName].set_head_config(arm = 2, config = 1) # Head Down
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 3) # Elevator to mid
    sleep(0.5)
    cs.robot[BotName].pumps_drop(ids = "2") # Drop the pumps
    print("Drop carrying : Done")

def run_movement():
    cs = init_bot()

    cs.robot[BotName].bumper_open()
    sleep(0.5)
    drop_carrying(cs) # Drop the carry statuette
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 5) # Elevator to store statuette
    sleep(0.5)
    cs.robot[BotName].set_head_config(arm = 2, config = 2) # Head to mid
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 3) # Elevator to mid
    sleep(0.5)
    cs.robot[BotName].pumps_get(ids = "2") # Pump the pump 2
    sleep(0.5)
    cs.trajman[BotName].move_trsl(acc = 200, dec = 200, dest = 95, maxspeed = 500, sens = 1) # Advance to 95
    sleep(0.5)
    cs.robot[BotName].goto(x = default_x, y = default_y)
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 5) # Elevator to store statuette
    sleep(0.5)
    cs.robot[BotName].pumps_get(ids = "4") # Pump the pump 4
    sleep(0.5)
    cs.robot[BotName].set_head_config(arm = 2, config = 0) # Head up
    sleep(0.5)
    #cs.robot[BotName].pumps_drop(ids = "2") # Drop the pumps
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 3) # Elevator to mid
    sleep(0.5)
    cs.robot[BotName].set_head_config(arm = 2, config = 1) # Head down
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 0) # Elevator to closed
    sleep(0.5)
    cs.trajman[BotName].move_trsl(acc = 200, dec = 200, dest = 100, maxspeed = 500, sens = 1) # Advance to 100
    sleep(0.5)
    cs.robot[BotName].pumps_get(ids = "2") # Pump the pump 2
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 3) # Elevator to gallery
    sleep(0.5)
    cs.robot[BotName].set_elevator_config(arm = 2, config = 0) # Elevator to closed
    sleep(0.5)
    cs.robot[BotName].snowplow_open()
    sleep(0.5)
    cs.trajman[BotName].move_trsl(acc = 200, dec = 200, dest = 90, maxspeed = 400, sens = 1) # Advance to 90
    sleep(0.5)
    cs.robot[BotName].pumps_drop(ids = "2") # Drop the pump 2
    sleep(0.5)
    move_side_arms("head", cs)
    sleep(0.5)
    move_side_arms("elevator_down", cs) # Activate arm movement func down
    sleep(0.5)
    move_side_arms("elevator_up", cs) # Activate arm movement func up
    sleep(0.5)
    cs.robot[BotName].goto(x = default_x, y = default_y)
    sleep(0.5)
    cs.robot[BotName].snowplow_close()
    sleep(0.5)
    cs.robot[BotName].bumper_close()
    sleep(0.5)
    input("Finished !")

if __name__ == "__main__":
    run_movement()