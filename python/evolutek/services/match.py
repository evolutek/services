from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib import ROBOT
from time import sleep

@Service.require('config')
@Service.require('gpios', ROBOT)
@Service.require('trajman', ROBOT)
class Match(Service):

    def __init__(self):

        # Cellaserv services
        self.config = cs.config
        self.gpios = cs.gpios[ROBOT]
        self.trajman = cs.trajman[ROBOT]

        # Color params
        self.color1 = self.config.get(section="match", option="color1")
        self.color2 = self.config.get(section="match", option="color2")

        # Beacon param
        self.url = self.config.get(section="beacon", option="url")
        self.refresh = self.config.get(section="beacon", option="refresh")

        # Match params
        self.color = None
        self.match_satus = 'unstarted'
        self.pal_position = None
        self.pmi_position = None
        self.robots = []
        self.front_detection = False
        self.back_detection = False
        self.front_detected = 0
        self.back_detected = 0
        self.score = 0
        self.tirette = 0

    @Service.thread
    def get_robots(self):
        while True:
            # Get robots
            self.publish('robots', self.pal_position, self.pmi_position, self.robots)
            sleep(float(self.refresh))

    @Service.thread
    def get_position(self):
        while True:
            pos = self.trajman.get_position()
            if ROBOT == 'pal':
                self.pal_position = pos
            else:
                self.pmi_position = pos
            self.publish(pos)
            sleep(float(self.refresh))

    @Service.event
    def match_start(self):
        self.match_status = "started"

    @Service.event
    def match_end(self):
        self.match_status = "ended"

    @Service.event
    def score(self, value):
        self.score += value

    @Service.event
    def front(self, name, id, value):
        print("Front detection from: (%s, %s) with: %s" % (name, id, value))
        if bool(value):
            if self.front_detected == 0:
                self.publish("front_detection")
            self.front_detected += 1
        else:
            if self.front_detected == 0:
                return
            if self.front_detected == 1:
                self.publish("front_end_detection")
            self.front_detected -= 1

    @Service.event
    def back(self, name, id, value):
        print("Back detection from: (%s, %s) with: %s" % (name, id, value))
        if bool(value):
            if self.back_detected == 0:
                self.publish("back_detection")
            self.back_detected += 1
        else:
            if self.back_detected == 0:
                return
            if self.back_detected == 1:
                self.publish("back_end_detection")
            self.back_detected -= 1

    @Service.event
    def tirette(self, name, id, value):
        print("Tirette: %s" % value)
        self.tirette = int(tirette)
        if self.tirette == 0:
            self.publish("match_start")
        else:
            self.publish("tirette_on")

    @Service.action
    def get_match(self):
        self.match = {}
        match['status'] = self.match_status
        match['color'] = self.color
        match['pal'] = self.pal_position
        match['pmi'] = self.pmi_position
        match['robots'] = self.robots
        match['front'] = self.front_detection
        match['back'] = self.back_detection
        match['score'] = self.score
        return match

    @Service.action
    def reset(self):
        self.color = self.color1 if int(self.gpios.read("color")) else self.color2
        self.match_status = 'unstarted'
        self.score = 0
        return self.color

def main():
    match = Match()
    match.run()

if __name__ == "__main__":
    main()
