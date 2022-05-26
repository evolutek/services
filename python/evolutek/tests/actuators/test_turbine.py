from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation

from time import sleep

acts = {
    9: [I2CActType.Servo, 180],
    10: [I2CActType.Servo, 180],
    11: [I2CActType.Servo, 180],
    12: [I2CActType.Servo, 180],
    15: [I2CActType.Servo, 180],
    8: [I2CActType.ESC, 0.5],
    13: [I2CActType.ESC, 0.5],
    14: [I2CActType.ESC, 0.5],
}

i2c_acts_handler = I2CActsHandler(acts, frequency=50)
print(i2c_acts_handler)

print("Test extend_right_vacuum:")
i2c_acts_handler[11].set_angle(96.4)

sleep(5)

for _ in range(3):
    print("Test turbine_on:")
    i2c_acts_handler[8].set_speed(0.1)

    sleep(2)

    print("Test turbine_low_power:")
    i2c_acts_handler[8].set_speed(0.06)

    sleep(2)

print("Test retract_right_vacuum:")
i2c_acts_handler[11].set_angle(160.7)

print("Test turbine_off:")
i2c_acts_handler[8].set_speed(0)

sleep(5)

i2c_acts_handler.free_all()
