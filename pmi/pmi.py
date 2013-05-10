#!/usr/bin/env python3

from time import sleep
from threading import Event, Timer, Thread
from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

DELAY = 0.2

### ALGO ###
# avancer et ramasser verre tant que < 4 ou bord de table
###

class Null:
    def __call__(self, **data):
        pass

    def __getattr__(self, name):
        return self

class PMI(Service):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cs = CellaservProxy()


        self.timer_stop = Timer(87, self.stop)
        self.worker = Thread(target=self.work)
        self.switch_event = Event()
        self.near_event = Event()
        self.line_event = Event()
        self.switchWorker = Thread(target=self.loop_switch)
        self.borderWorker = Thread(target=self.loop_border)
        self.nearWorker = Thread(target=self.loop_near)
        self.lineWorker = Thread(target=self.pmi_line)

        self.is_stopped = Event()
        self.glass_ready_event1 = Event()
        self.glass_ready_event2 = Event()
        self.border_event = Event()
        self.null = Null()

    def apmi_check(self):
        if self.is_stopped.is_set():
            print("stopped")
            return self.null
        else:
            return self.cs.apmi

    @Service.event
    def glass_ready1(self):
        self.glass_ready_event1.set()

    @Service.event
    def glass_ready2(self):
        self.glass_ready_event2.set()

    @Service.event
    def border(self):
        print("Border")
        sleep(DELAY)
        self.cs.apmi.move(s=500, d=0)
        sleep(2)
        self.cs.apmi.move(s=0)
        sleep(2)
        self.count = -1
        self.cs.apmi.lift(p=0)
        sleep(2)
        self.border_event.set()

    @Service.action
    def test(self):
        self.cs.apmi.move(d=1, s=300)
        sleep(1)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.move(d=0, s=300)
        sleep(1)
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.lift(p=0)
        sleep(DELAY)
        self.cs.apmi.lift(p=950)
        sleep(1)
        self.cs.apmi.lift(p=0)
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(1)
        self.cs.apmi.pliers(a="close")
        sleep(1)
        self.cs.apmi.pliers(a="open")
        sleep(1)

    @Service.action
    def start(self, color):
        self.count = 0
        self.first_stack_done = False
        self.second_stack_done = False
        self.first = True
        self.isWorking = False
        self.opposit_side = "right" if color == "blue" else "left"
        print("timer")
        self.is_stopped.clear()
        self.timer_stop.start()
        print("worker")
        self.worker.start()
        self.switchWorker.start()
        self.borderWorker.start()
        self.nearWorker.start()
        self.lineWorker.start()

    def work(self):
        self.push_cherries()
        self.glass_ready_event1.wait()
        print("GO TO WALL de 112")
        self.go_to_wall()

    # longe le mur droit
    def go_to_wall(self):
        if self.second_stack_done:
            return
        print("go to wall")
        sleep(DELAY)
        self.apmi_check().lift(p=0)
        sleep(DELAY)
        self.apmi_check().pliers(a="open")
        sleep(DELAY)
        self.apmi_check().move(d=1, s=1023, w=self.opposit_side)

    # gere les interruptions
    @Service.event
    def switch(self, state):
        self.state = state
        self.switch_event.set()

    @Service.event
    def pmi_near(self):
        self.near_event.set()

    @Service.event
    def line(self):
        self.line_event.set()

    def pmi_line(self):
        self.line_event.wait()
        self.cs.apmi.move(s=500, d=1)
        sleep(4)
        self.cs.apmi.move(s=0)

    def loop_switch(self):
        while True:
            # check switch_event or < 300
            self.switch_event.wait()
            self.switch_event.clear()

            if self.state == 1 and (not self.isWorking):
                self.is_working = True
                self.take_glass()

                if (self.count == 4):  # and not self.first_stack_done
                    print("4 verres !")
                    if(self.first_stack_done == False):
                        self.drop_first_stack()
                        self.glass_ready_event2.wait()
                        self.go_to_wall()
                        print("GO TO WALL 145")
                    else:
                        self.drop_second_stack()
                elif self.count >= 0:  # continuer d'avancer
                    print("GO TO OPPOSIT SIDE")
                    self.apmi_check().move(d=1, s=1023, w=self.opposit_side)
                else:
                    self.glass_ready_event2.wait()
                    if self.first == True:
                        print("GO TO WALL 152")
                        self.go_to_wall()
                        self.first = False

                self.is_working = False

    def loop_border(self):
        while True:
            self.border_event.wait()
            self.border_event.clear()
            if(self.first_stack_done == False):
                self.drop_first_stack()
            else:
                self.cs.apmi.move(s=0)
                self.drop_second_stack()
            self.is_working = False

    def loop_near(self):
        return
        #while True:
        #    print("Wait")
        #    self.near_event.wait()
        #    print("done")
        #    self.cs.apmi.move(s=0)
        #    import os
        #    os.system("kill {}".format(os.getpid()))

    def take_glass(self):
        print("glass")
        if self.count == -1:
            print("ignore")
            return
        if self.count > 0:
            sleep(2)
        self.apmi_check().pliers(a="open")
        sleep(0.5)

        if self.count < 3:
            self.apmi_check().lift(p=0)
            sleep(1.5)
            self.apmi_check().pliers(a="close")
            sleep(DELAY)
            self.apmi_check().lift(p=950)
            sleep(1.5)
        else:
            self.apmi_check().lift(p=300)
            sleep(0.5)
            self.apmi_check().pliers(a="close")
            sleep(1)
            self.apmi_check().lift(p=360)
            sleep(DELAY)
        self.count += 1

    def drop_first_stack(self):
        #self.apmi_check().lift(p=360)
        #sleep(DELAY)
        print("Drop first stack")
        self.apmi_check().move(d=0, s=1023)
        # FIXME hokuyo
        sleep(2)
        self.cs("stack")
        sleep(2)
        self.apmi_check().move(s=0)
        sleep(1)
        try:
            self.apmi_check().rotate(s=self.opposit_side, d=0, a=70)
        except:
            pass
        sleep(2)
        self.apmi_check().move(d=1, s=500)
        sleep(3)
        self.apmi_check().move(s=0)
        sleep(1)
        self.apmi_check().pliers(a="open")
        sleep(1)
        self.apmi_check().move(d=0, s=500)
        sleep(3)
        self.apmi_check().move(s=0)
        sleep(1)
        self.apmi_check().rotate(s=self.opposit_side, d=1, a=60)
        sleep(2)
        self.count = 0
        self.first_stack_done = True

    def drop_second_stack(self):
        self.second_stack_done = True
        print("Drop second stack")
        self.apmi_check().move(s=0)
        sleep(1)
        self.apmi_check().pliers(a="open")
        sleep(1)
        self.apmi_check().move(s=500, d=0)
        sleep(2)
        self.apmi_check().move(s=0, d=0)
        exit(0)

    def push_cherries(self):
        sleep(DELAY)
        self.apmi_check().move(s=500, d=0)
        sleep(7)
        self.apmi_check().move(s=0)
        sleep(DELAY)

    def stop(self):
        print("Stop")
        self.is_stopped.set()
        self.cs.apmi.move(s=0)
        sleep(DELAY)
        self.cs.apmi.lift(p=0)
        sleep(2)
        self.cs.apmi.pliers(a="open")

def main():
    pmi = PMI()
    pmi.run()


if __name__ == '__main__':
    main()
