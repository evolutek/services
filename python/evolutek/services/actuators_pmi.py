import cellaserv.proxy
import mraa
from cellaserv.service import Service
from time import sleep

@Service.require("ax", "10")
@Service.require("ax", "11")
@Service.require("ax", "12")
@Service.require("ax", "13")
class actuators(Service):

    def __init__(self):
        super().__init__(identification=str('pmi'))
        self.robot = cellaserv.proxy.CellaservProxy()
        for n in [10, 11, 12, 13]:
            self.robot.ax[str(n)].mode_joint()
        self.enb = mraa.Pwm(5)
        in3 = mraa.Gpio(8)
        in4 = mraa.Gpio(9)
        in3.dir(mraa.DIR_OUT)
        in4.dir(mraa.DIR_OUT)
        in3.write(True)
        in4.write(False)
        self.init_all()
        print("Actuators : Init Done")

    @Service.action
    def init_all(self):
        self.move_arm()
        self.close_bee_arm()
        self.robot.ax["11"].move(goal=900)
        self.robot.ax["10"].move(goal=130)
        self.enb.period_ms(4)
        self.enb.enable(True)

    @Service.action
    def move_arm(self, percent=0):
        self.robot.ax["12"].move(goal=(460 + int((int(percent)/100) * 305)))

    @Service.action
    def open_bee_arm(self):
        self.robot.ax["13"].move(goal=512)

    @Service.action
    def close_bee_arm(self):
        self.robot.ax["13"].move(goal=200)

    @Service.action
    def dump_balls(self, nb=1, color="green"):
        if nb == 1:
            ax =  11 if color == "green" else 10
            self.robot.ax[str(ax)].move(goal=512)
            #self.enable_canon(True)
            for i in range(8):
                self.robot.ax[str(ax)].move(goal= 670 if ax == 11 else  380)
                sleep(2)
                self.robot.ax[str(ax)].move(goal=512)
                if i != 8:
                    sleep(1)
            #self.enable_canon(True)
        else:
            ax = 11 if color != "green"  else 10
            self.robot.ax[str(ax)].move(goal=512)
            for i in range(8):
                if i % 2:
                    self.robot.ax[str(ax)].move(goal=(670 if ax == 11 else 380))
                else:
                    self.robot.ax[str(ax)].move(goal=(670 if ax != 11 else 380))
                sleep(2)
                self.robot.ax[str(ax)].move(goal=512)
                if i != 8:
                    sleep(1)
    
    @Service.action
    def enable_canon(self, status):
        if status:
            self.enb.write(0.48)
        else:
            self.enb.write(0)



def main():
    actuators_pal = actuators()
    Service.loop()

if __name__ == "__main__":
    main()
