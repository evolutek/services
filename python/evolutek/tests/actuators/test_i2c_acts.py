from evolutek.lib.actuators.i2c_acts import I2CActsHandler, I2CActType, ESCVariation

from time import sleep

acts = {
    0: [I2CActType.Servo, 180],
    1: [I2CActType.Servo, 180],
    14: [I2CActType.ESC, 0.3],
    15: [I2CActType.ESC, 0.3],
}


i2c_acts_handler = I2CActsHandler(acts, frequency=50)
print(i2c_acts_handler)


i2c_acts_handler[0].set_angle(0)
i2c_acts_handler[1].set_angle(180)
sleep(2)
i2c_acts_handler[0].set_angle(180)
i2c_acts_handler[1].set_angle(0)
sleep(2)
i2c_acts_handler[14].set_speed(0.3)
sleep(2)
i2c_acts_handler[14].set_speed(0.0)
i2c_acts_handler[15].set_speed(0.3)
sleep(2)
i2c_acts_handler[15].set_speed(0.0)
sleep(2)
i2c_acts_handler.free_all()
