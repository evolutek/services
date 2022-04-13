from evolutek.lib.actuators.servo import ServoHandler

from time import sleep

pumps = {
    0: [
           0,
            33,
            180
    ]
}


servo_controller = ServoHandler(pumps, 1)
print(servo_controller)

for servo in servo_controller:
    servo_controller[servo].set_angle(180)
    sleep(1)
    servo_controller[servo].set_angle(0)
