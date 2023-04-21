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
i2c_acts_handler.set_speed(13, 0.2)
i2c_acts_handler.set_speed(14, 0.2)

print("Test canon_off:")
i2c_acts_handler.set_speed(13, 0)
i2c_acts_handler.set_speed(14, 0)

print("Test turbine_on:")
i2c_acts_handler.set_speed(8, 0.3)

print("Test turbine_low_power:")
i2c_acts_handler.set_speed(8, 0.07)

print("Test turbine_off:")
i2c_acts_handler.set_speed(8, 0)

print("Test extend_left_vacuum:")
i2c_acts_handler.set_angle(10, 83.6)

print("Test retract_left_vacuum:")
i2c_acts_handler.set_angle(10, 19.3)

print("Test extend_right_vacuum:")
i2c_acts_handler.set_angle(11, 160.7)

print("Test retract_right_vacuum:")
i2c_acts_handler.set_angle(11, 96.4)

print("Test clamp_open:")
i2c_acts_handler.set_angle(9, 0)
i2c_acts_handler.set_angle(15, 180)

print("Test clamp_open_half:")
i2c_acts_handler.set_angle(9, 9.6)
i2c_acts_handler.set_angle(15, 170.3)

print("Test clamp_close:")
i2c_acts_handler.set_angle(9, 19.3)
i2c_acts_handler.set_angle(15, 160.7)

print("Test push_canon:")
i2c_acts_handler.set_angle(12, 180)

print("Test push_tank:")
i2c_acts_handler.set_angle(12, 51.4)

print("Test push_drop:")
i2c_acts_handler.set_angle(12, 173.6)

i2c_acts_handler.free_all()
