import cellaserv.proxy

from cellaserv.service import Service
from time import sleep

@Service.require("ax", "10")
@Service.require("ax", "11")
@Service.require("ax", "12")
class actuators(Service):

    def __init__(self):
        super().__init__(identification=str('pal'))
        self.robot = cellaserv.proxy.CellaservProxy()
        for n in [10, 11, 12]:
            self.robot.ax[str(n)].mode_joint()
        self.init__all()
        print("Actuators : Init Done")

    def init__all(self):
        self.move_arm()
        self.robot.ax["11"].move(goal=900)
        self.robot.ax["10"].move(goal=130)

    @Service.action
    def move_arm(self, pourcentage=0):
        self.robot.ax["12"].move(goal=(460 + int((int(pourcentage)/100) * 305)))

    @Service.action
    def dump_balls(self, nb=1, color="green"):
        if nb == 1:
            ax =  11 if color == "green" else 10
            self.robot.ax[str(ax)].move(goal=512)
            #TODO start_canon
            for i in range(8):
                self.robot.ax[str(ax)].move(goal= 670 if ax == 11 else  380)
                sleep(2)
                self.robot.ax[str(ax)].move(goal=512)
                if i != 8:
                    sleep(1)
            #TODO stop_canon
        else:
            ax = 11 if color != "green"  else 10
            self.robot.ax[str(ax)].move(goal=512)
            #TODO start_canon
            for i in range(8):
                if i % 2:
                    self.robot.ax[str(ax)].move(goal=(670 if ax == 11 else 380))
                else:
                    self.robot.ax[str(ax)].move(goal=(670 if ax != 11 else 380))
                sleep(2)
                self.robot.ax[str(ax)].move(goal=512)
                if i != 8:
                    sleep(1)

def main():
    actuators_pal = actuators()
    Service.loop()

if __name__ == "__main__":
    main()
