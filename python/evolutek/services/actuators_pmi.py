import cellaserv.proxy
import mraa
from cellaserv.service import Service
from time import sleep

@Service.require("ax", "1")
@Service.require("ax", "2")
@Service.require("ax", "3")
@Service.require("ax", "4")
class actuators(Service):

    def __init__(self):
        super().__init__(identification=str('pmi'))
        self.robot = cellaserv.proxy.CellaservProxy()
        for n in [1, 2, 3, 4]:
            self.robot.ax[str(n)].mode_joint()
        self.init_all()
        print("Actuators : Init Done")

    @Service.action
    def init_all(self):
        self.close_arm()

    @Service.action
    def open_arm(self):
        self.robot.ax["4"].move(goal=850)

    @Service.action
    def close_arm(self):
        self.robot.ax["4"].move(goal=550)

def main():
    actuators_pmi = actuators()
    Service.loop()

if __name__ == "__main__":
    main()
