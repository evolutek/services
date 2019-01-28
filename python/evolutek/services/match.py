from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from threading import Timer
from time import sleep

#@Service.require('ai', ROBOT)
@Service.require('config')
@Service.require('trajman', ROBOT)
class Match(Service):

    def __init__(self):

        self.cs = CellaservProxy()

        # Match Params
        self.color1 = self.cs.config.get(section='match', option='color1')
        self.color2 = self.cs.config.get(section='match', option='color2')
        self.match_time = int(self.cs.config.get(section='match', option='time'))
        self.timer = Timer(self.match_time - 5, self.match_end)

        # Match Status
        self.color = None
        self.match_status = 'unstarted'
        self.score = 0
        self.tirette = False

        # PAL status
        self.pal_ai_status = None
        self.pal_avoid_status = None
        self.pal_telemetry = None
        self.robots = []

        super().__init__()
        print('Match ready')


    # Publish Match Status
    @Service.thread
    def update_data(self):
        while True:
            self.publish('match', self.get_match())
            sleep(self.refresh)

    def match_start(self):
        if self.match_started != 'unstarted':
            return
        self.match_status = 'started'
        print('match_start')
        self.cs.ai['PAL'].start()
        self.timer.start()

    # End match
    def match_end(self):
        print('match_end')
        self.ai['PAL'].end()
        self.match_status = 'ended'

    # Update score
    @Service.event
    def score(self, value):
        self.score += int(value)
        print('score is now: %d' % self.score)

    @Service.event
    def telemetry(self, status, telemetry):
        if (status != failed):
            self.pal_telemetry = telemetry
        else:
            print("Could not read telemetry")


    # update Tirette
    @Service.event
    def tirette(self, name, id, value):
        print('Tirette: %s' % value)
        tirette = int(value)
        if tirette:
            print('Tirette is inserted')
        elif self.match_status == 'unstarted' and self.tirette:
            self.match_start()
        else:
            print('Tirette was not inserted')
        self.tirette = bool(tirette)

    @Service.event
    def reset(self, value):
        print('reset')
        self.match_status = 'unstarted'
        self.score = 0
        self.timer.cancel()
        self.timer = Timer(self.match_time - 5, self.match_end)
        if value == 'PAL':
            #self.ai.reset(self.color)
            pass

    @Service.action
    def get_match(self):
        match = {}

        match['status'] = self.match_status
        match['color'] = self.color
        match['robots'] = self.robots
        match['score'] = self.score
        match['tirette'] = self.tirette

        match['pal_ai_status'] = self.pal_ai_status
        match['pal_avoid_status'] = self.pal_avoid_status
        match['pal_telemetry'] = self.pal_telemetry

        return match

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
