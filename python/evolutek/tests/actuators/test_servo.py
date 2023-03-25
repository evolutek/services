from evolutek.lib.actuators.servo import ServoHandler

from time import sleep

servos = {
        0: [ 333, 57.5],
        1: [ 50, 45],
        14: [50, 45],
        15: [333, 57.5]
}


servo_controller = ServoHandler(servos)
print(servo_controller)

servo_controller.set_angle_all({0: 0, 1:0, 14: 25, 15:57.5})
servo_controller.set_angle_all({0:57.5, 1: 25, 14:0, 15: 0})
