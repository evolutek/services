from evolutek.lib.actuators.servo import ServoHandler

from time import sleep

pumps = {
        0: [ 333, 57.5],
        1: [ 50, 45],
        14: [50, 45],
        15: [333, 57.5]
}


servo_controller = ServoHandler(pumps, 1)
print(servo_controller)

"""for servo in servo_controller:
    servo_controller[servo].set_angle(180)
    sleep(1)
    servo_controller[servo].set_angle(0)
    """


#servo_controller.set_angle_all({14:0})

servo_controller.set_angle_all({0: 0, 1:0, 14: 25, 15:57.5})
servo_controller.set_angle_all({0:57.5, 1: 25, 14:0, 15: 0})
