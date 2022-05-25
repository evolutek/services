from evolutek.lib.actuators.i2c_acts.py import I2CActsHandler, I2CActType, ESCVariation

from time import sleep

servos = {
        0: [180],
        1: [180]
}

escs = {
    14: {
        "max_range": 0.3
    },
    15: {
        "max_range": 0.3,
        "esc_variation": ESCVariation.Emax
    }
}


i2c_acts_handler = I2CActsHandler(servos | escs, frequency=50)
print(i2c_acts_handler)


i2c_acts_handler[0].set_angle(0)
i2c_acts_handler[1].set_angle(180)
sleep(1)
i2c_acts_handler[0].set_angle(180)
i2c_acts_handler[1].set_angle(0)
sleep(1)
i2c_acts_handler[14].set_speed(0.3)
sleep(1)
i2c_acts_handler[14].set_speed(0.0)
i2c_acts_handler[15].set_speed(0.3)
sleep(1)
i2c_acts_handler[15].set_speed(0.0)
sleep(1)
for act in i2c_acts_handler:
    act.free()