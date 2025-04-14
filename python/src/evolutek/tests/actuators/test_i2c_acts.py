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

print("Test canon_on:")
i2c_acts_handler[13].set_speed(0.4)
i2c_acts_handler[14].set_speed(0.4)

sleep(5)

print("Test canon_off:")
i2c_acts_handler[13].set_speed(0)
i2c_acts_handler[14].set_speed(0)

sleep(5)

print("Test turbine_on:")
i2c_acts_handler[8].set_speed(0.1)

sleep(5)

print("Test turbine_low_power:")
i2c_acts_handler[8].set_speed(0.06)

sleep(5)

print("Test turbine_off:")
i2c_acts_handler[8].set_speed(0)

sleep(5)

print("Test extend_left_vacuum:")
i2c_acts_handler[10].set_angle(83.6)

sleep(5)

print("Test retract_left_vacuum:")
i2c_acts_handler[10].set_angle(19.3)

sleep(5)

print("Test extend_right_vacuum:")
i2c_acts_handler[11].set_angle(96.4)

sleep(5)

print("Test retract_right_vacuum:")
i2c_acts_handler[11].set_angle(160.7)

sleep(5)

print("Test clamp_open:")
i2c_acts_handler[9].set_angle(0)
i2c_acts_handler[15].set_angle(180)

sleep(5)

print("Test clamp_open_half:")
i2c_acts_handler[9].set_angle(9.6)
i2c_acts_handler[15].set_angle(170.3)

sleep(5)

print("Test clamp_close:")
i2c_acts_handler[9].set_angle(19.3)
i2c_acts_handler[15].set_angle(160.7)

sleep(5)

print("Test push_canon:")
i2c_acts_handler[12].set_angle(180)

sleep(5)

print("Test push_tank:")
i2c_acts_handler[12].set_angle(51.4)

sleep(5)

print("Test push_drop:")
i2c_acts_handler[12].set_angle(173.6)

sleep(5)

i2c_acts_handler.free_all()
