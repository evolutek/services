from evolutek.lib.actuators.servo import ServoHandler

from time import sleep

pumps = {
    0: [
            3333,
            180
    ],
    11: [
        50,
        180,
    ],
    15: [
        333,
        180
    ]

}


servo_controller = ServoHandler(pumps, 1)
print(servo_controller)

"""for servo in servo_controller:
    servo_controller[servo].set_angle(180)
    sleep(1)
    servo_controller[servo].set_angle(0)
    """
servo_controller.set_angle_all({0: 180, 11:180, 15:180})
sleep(1)
servo_controller.set_angle_all({0:0, 11:0, 15:0})
