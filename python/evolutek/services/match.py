from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.gpio.gpio_factory import create_gpio, GpioType

from enum import Enum
from threading import Timer
from time import sleep, time

WEATHERCOCK_TIME = 25 # Time (sec) between the match start and the weathercock reading
WEATHERCOCK_GPIO = 24 # Number of the GPIO used by the weathercock reader

class MatchStatus(Enum):
    unstarted = "Unstarted"
    started = "Started"
    ended = "Ended"

# Service class for the match
@Service.require("config")
class Match(Service):

    def __init__(self):

        super().__init__()
        self.cs = CellaservProxy()

        # Get the config of the match
        match_config = self.cs.config.get_section('match')
        self.color1 = match_config['color1']
        self.color2 = match_config['color2']
        self.match_duration = int(match_config['duration'])

        # Match Status
        self.match_status = MatchStatus.unstarted
        self.color = None
        self.set_color(self.color1)
        self.score = 0
        self.start_time = 0
        self.anchorage = None

        print('[MATCH] Match ready')

    """ EVENT """

    """ Update score """
    @Service.event('score')
    def set_score(self, value=0):
        if self.match_status != MatchStatus.started:
            return
        self.score += int(value)
        print('[MATCH] score is now: %d' % self.score)

    """ Tirette """
    @Service.event('tirette')
    def match_start(self, name='', id=0, value=0):

        if self.match_status != MatchStatus.unstarted or self.color is None:
            return

        self.start_time = time()

        self.publish('match_start')
        match_timer = Timer(self.match_duration, self.match_end)
        match_timer.start()
        self.match_status = MatchStatus.started
        print('[MATCH] Match start')

        # Reads the weathercock position 25 seconds after the start of the match
        weathercock_timer = Timer(WEATHERCOCK_TIME, self.read_weathercock)
        weathercock_timer.start()

        flags_timer = Timer(self.match_duration - 2, self.raise_flags)
        flags_timer.start()

    """ WeatherCock """
    def read_weathercock(self):
        print('[MATCH] reading weathercock position')
        white = create_gpio(WEATHERCOCK_GPIO, 'weathercock', dir=False, type=GpioType.RPI).read()
        side = 'north' if not white else 'south'
        self.publish('anchorage', side=(side))
        self.anchorage = side

    """ Raise flags """
    def raise_flags(self):
        print('[MATCH] Raising flags')
        self.publish('raise_flags')
        self.set_score(value=10) # Adds 10 points

    """ ACTION """

    """ Reset match """
    @Service.action
    def reset_match(self, color=None):
        if self.match_status == MatchStatus.started:
            print("[MATCH] Can't reset match, match is running")
            return False

        print('[MATCH] Reset match')
        self.match_status = MatchStatus.unstarted
        self.score = 0

        if not self.set_color(color):
            self.color = self.color1

        return True

    """ Get color """
    @Service.action
    def get_color(self):
        return self.color

    """ Set color """
    @Service.action
    def set_color(self, color):
        if color != self.color1 and color != self.color2:
            print('[MATCH] Invalid color')
            return False

        if self.match_status == MatchStatus.started:
            print("[MATCH] Can't set color, match is running")

        self.color = color

        self.publish('match_color', color=self.color)
        return True

    """ Get match """
    @Service.action
    def get_status(self):
        match = {}

        match['status'] = self.match_status.value
        match['color'] = self.color
        match['score'] = self.score
        match['time'] = time() - self.start_time

        return match

    """ GET anchorage """
    @Service.action
    def get_anchorage(self):
        return self.anchorage

    """ End match """
    @Service.action
    def match_end(self):
        self.publish('match_end')
        self.match_status = MatchStatus.ended
        print('[MATCH] Match End')

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
