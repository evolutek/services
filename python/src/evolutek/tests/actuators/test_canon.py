from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation

from time import sleep

acts = {
    9: [I2CActType.Servo, 180],
    10: [I2CActType.Servo, 180],
    11: [I2CActType.Servo, 180],
    12: [I2CActType.Servo, 180],
    15: [I2CActType.Servo, 180],
    8: [I2CActType.ESC, 0.3],
    13: [I2CActType.ESC, 0.3],
    14: [I2CActType.ESC, 0.3],
}

i2c_acts_handler = I2CActsHandler(acts, frequency=50)
print(i2c_acts_handler)

print("Test canon_on:")
i2c_acts_handler[13].set_speed(0.3)
i2c_acts_handler[14].set_speed(0.3)

sleep(3)

i2c_acts_handler[13].set_speed(0.2)
i2c_acts_handler[14].set_speed(0.2)

sleep(3)

i2c_acts_handler[13].set_speed(0.1)
i2c_acts_handler[14].set_speed(0.1)

sleep(3)

print("Test canon_off:")
i2c_acts_handler[13].set_speed(0)
i2c_acts_handler[14].set_speed(0)

i2c_acts_handler.free_all()
