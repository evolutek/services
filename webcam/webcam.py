from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

class Webcam(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cs = CellaservProxy(self)

    @Service.action
    def porte(self):
        self.cs.ax.move(ax=3, goal=530)
        self.cs.ax.move(ax=5, goal=810)

    @Service.action
    def table(self):
        self.cs.ax.move(ax=3, goal=590)
        self.cs.ax.move(ax=5, goal=550)

    @Service.action
    def schischi(self):
        self.cs.ax.move(ax=3, goal=680)
        self.cs.ax.move(ax=5, goal=570)

def main():
    webcam = Webcam()
    webcam.run()

if __name__ == '__main__':
    main()
