from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.settings import ROBOT
from threading import Timer
from time import sleep

#@Service.require('ai', ROBOT)
@Service.require('config')
#@Service.require('gpios', ROBOT)
@Service.require('trajman', ROBOT)
class Match(Service):

    def __init__(self):

        self.cs = CellaservProxy()
        # Cellaserv services
        #self.ai = self.cs.ai[ROBOT]
        self.config = self.cs.config
        #self.gpios = self.cs.gpios[ROBOT]
        self.trajman = self.cs.trajman[ROBOT]

        # Color params
        self.color1 = self.config.get(section='match', option='color1')
        self.color2 = self.config.get(section='match', option='color2')

        # Match timer
        self.match_time = self.config.get(section='match', option='time')
        self.timer = Timer(int(self.match_time) - 5, self.match_end)

        # Beacon param
        self.url = self.config.get(section='beacon', option='url')
        self.refresh = float(self.config.get(section='beacon', option='refresh'))

        # Tirette security
        self.tirette_inserted = False

        # Match params
        self.color = None
        self.match_status = 'unstarted'
        self.position = None
        self.direction = None
        self.robots = []
        self.front_detected = 0
        self.back_detected = 0
        self.score = 0
        self.tirette = False

        super().__init__(identification=ROBOT)

        print('Match ready')


    # Pull robots positions
    @Service.thread
    def update_data(self):
        while True:
            # Get robots
            #self.publish('robots', self.robots)

            # Update position
            self.position = self.trajman.get_position()
            self.publish('position', value=self.position)

            # Update moving direction
            vector = self.trajman.get_vector_trsl()
            if vector['trsl_vector'] > 0.0:
                self.direction = True
            elif vector['trsl_vector'] < 0.0:
                self.direction = False
            else:
                self.direction = None
            self.publish('direction', value=self.direction)

        sleep(1)

    # Start match
    def match_start(self):
        print('match_start')
        #self.ai.start()
        self.timer.start()
        self.match_status = 'started'

    # End match
    def match_end(self):
        print('match_end')
        #self.ai.end()
        self.match_status = 'ended'

    # Update score
    @Service.event
    def score(self, value):
        self.score += int(value)
        print('score is now: %d' % self.score)

    # Update front detection
    @Service.event
    def front(self, name, id, value):
        print('Front detection from: (%s, %s) with: %s' % (name, id, value))
        if int(value):
            if self.front_detected == 0:
                self.publish('front_detection')
            self.front_detected += 1
        else:
            if self.front_detected == 0:
                return
            if self.front_detected == 1:
                self.publish('front_end_detection')
            self.front_detected -= 1

    # Update back detection
    @Service.event
    def back(self, name, id, value):
        if int(value):
            if self.back_detected == 0:
                self.publish('back_detection')
            self.back_detected += 1
        else:
            if self.back_detected == 0:
                return
            if self.back_detected == 1:
                self.publish('back_end_detection')
            self.back_detected -= 1

    # update Tirette
    @Service.event
    def tirette(self, name, id, value):
        print('Tirette: %s' % value)
        self.tirette = int(value)
        if self.tirette:
            self.tirette_inserted =  True
            print('Tirette is inserted')
        elif self.match_status == 'unstarted' and self.tirette_inserted:
            self.match_start()
        else:
            print('Tirette was not inserted')

    @Service.event
    def reset(self):
        print('reset')
        #self.color = self.color1 if int(self.gpios.read('color')) else self.color2
        self.match_status = 'unstarted'
        self.score = 0
        self.tirette_inserted = False
        #self.ai.reset(self.color)

    @Service.action
    def get_match(self):
        match = {}
        match['status'] = self.match_status
        match['color'] = self.color
        match['direction'] = self.direction
        match['position'] = self.position
        match['robots'] = self.robots
        match['front'] = self.front_detected
        match['back'] = self.back_detected
        match['score'] = self.score
        match['tirette'] = self.tirette
        return match

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
