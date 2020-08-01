from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.watchdog import Watchdog

from enum import Enum
from threading import Timer, Thread
from time import sleep

class MatchStatus(Enum):
    unstarted = "Unstarted"
    started = "Started"
    ended = "Ended"

@Service.require("config")
class Match(Service):

    def __init__(self):

        super().__init__()
        self.cs = CellaservProxy()

        match_config = self.cs.config.get_section('match')
        self.color1 = match_config['color1']
        self.color2 = match_config['color2']
        self.match_duration = int(match_config['duration'])
        self.refresh = float(match_config['refresh'])
        self.timeout_robot = float(match_config['timeout_robot'])

        # Match Status
        self.color = self.color1
        self.match_status = MatchStatus.unstarted
        self.score = 0
        self.timer = Timer(self.match_duration, self.match_end)
        self.match_time = 0
        self.match_time_thread = Thread(target=self.match_time_loop)

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
    def match_start(self, name, id, value):
        if self.match_status != MatchStatus.unstarted or self.color is None:
            return

        self.publish('match_start')
        self.timer.start()
        self.match_status = MatchStatus.started
        print('[MATCH] Match start')
        self.match_time_thread.start()

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
        self.timer = Timer(self.match_duration, self.match_end)
        self.match_time = 0
        self.match_time_thread = Thread(target=self.match_time_loop)

        if not self.set_color(color):
            self.color = None

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
        match['time'] = self.match_time

        return match

    """ End match """
    @Service.action
    def match_end(self):
        self.publish('match_end')
        self.match_status = MatchStatus.ended
        print('[MATCH] Match End')


    """ THREAD """

    """ Match status thread """
    @Service.thread
    def match_status(self):
      while True:
        self.publish('match_status', status=self.get_status())
        sleep(self.refresh)

    def match_time_loop(self):
        while self.match_status == MatchStatus.started:
            self.match_time += 1
            sleep(1)


def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
