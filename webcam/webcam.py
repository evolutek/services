from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

class Webcam(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)
        self.ax3 = self.cs.ax[3]
        self.ax5 = self.cs.ax[5]

    @Service.action
    def porte(self):
        self.ax3.move(goal=530)
        self.ax5.move(goal=810)

    @Service.action
    def table(self):
        self.ax3.move(goal=590)
        self.ax5.move(goal=550)

    @Service.action
    def schischi(self):
        self.ax3.move(goal=680)
        self.ax5.move(goal=570)

    @Service.action
    def charly(self):
        self.ax3.move(goal=530)
        self.ax5.move(goal=660)

    @Service.action
    def plafond(self):
        self.ax3.move(goal=400)
        self.ax5.move(goal=650)

    @Service.action
    def yoopo(self):
        self.ax3.move(goal=570)
        self.ax5.move(goal=830)

def main():
    webcam = Webcam()
    webcam.run()

if __name__ == '__main__':
    main()
