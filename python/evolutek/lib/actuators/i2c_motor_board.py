import board
import busio
import struct

from evolutek.lib.component import Component, ComponentsHolder


class I2CMotorBoardComponent(Component):
    def __init__(self, motor_board: "I2CMotorBoard", id: int, name: str):
        super().__init__(name, id)
        self.motor_board = motor_board


class I2CMotorBoard(ComponentsHolder):
    def __init__(self, components: list[tuple[type, list]], device_addr: int = 0x69):
        self.i2c = None
        self.device_addr = device_addr
        super().__init__('I2CMotorBoard', components, self._instantiate_component)

    def _instantiate_component(self, _, type: type[I2CMotorBoardComponent], args: list) -> I2CMotorBoardComponent:
        return type(self, *args)

    def _initialize(self):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
        except:
            print('[%s] Failed to init busio I2C' % self.name)
            return False
        return True

    def send_command(self, cmd_id: int, stepper_id: int, data: bytes):
        self.i2c.writeto(self.device_addr, bytes([cmd_id, stepper_id]) + data)


class I2CMotorBoardStepper(I2CMotorBoardComponent):
    def __init__(self, motor_board: I2CMotorBoard, stepper_id: int):
        self.stepper_id = stepper_id
        super().__init__(motor_board, stepper_id, f"stepper_{stepper_id}")

    def _initialize(self) -> bool:
        return True

    def __str__(self):
        return f"Id: {self.stepper_id}"

    def goto(self, steps: int, speed: int) -> bool:
        if speed < 0:
            return False

        if steps < -0x7FFFFFFF or steps > 0x7FFFFFFF:
            return False

        self.motor_board.send_command(0x02, self.stepper_id, struct.pack(">iI", steps, speed))

        return True

    def move(self, steps: int, speed: int) -> bool:
        self.motor_board.send_command(0x03, self.stepper_id, struct.pack(">iI", steps, speed))
        return True

    def home(self) -> bool:
        self.motor_board.send_command(0x01, self.stepper_id, bytes())
        return True
