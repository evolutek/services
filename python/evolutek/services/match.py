from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service
from evolutek.lib.match_interface import MatchInterface
from evolutek.lib.watchdog import Watchdog
from evolutek.lib.waiter import waitBeacon, waitConfig
from threading import Timer, Thread
from time import sleep

@Service.require("config")
class Match(Service):

    def __init__(self):

        self.cs = CellaservProxy()
        # Match Params
        match_config = self.cs.config.get_section('match')
        self.color1 = match_config['color1']
        self.color2 = match_config['color2']
        self.match_duration = int(match_config['duration'])
        self.refresh = float(match_config['refresh'])
        self.interface_enabled = match_config['interface_enabled']
        self.timeout_robot = float(match_config['timeout_robot'])

        # Match Status
        self.color = None
        self.match_status = 'unstarted'
        self.score = 0
        self.timer = Timer(self.match_duration, self.match_end)
        self.match_time = 0
        self.match_time_thread = Thread(target=self.match_time_loop)

        # PAL status
        self.pal_ai_s = None
        self.pal_telem = None
        self.pal_path = []
        self.pal_watchdog = Watchdog(self.timeout_robot * 1.5, self.reset_pal_status)

        # PMI status
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_path = []
        self.pmi_watchdog = Watchdog(self.timeout_robot * 1.5, self.reset_pmi_status)

        # Oppenents positions
        self.robots = []
        self.robots_watchdog = Watchdog(self.timeout_robot * 3, self.reset_robots)

        super().__init__()
        print('[MATCH] Match ready')


    """ MATCH UTILITIES """

    def reset_pal_status(self):
        self.pal_ai_s = None
        self.pal_telem = None
        self.pmi_path = []

    def reset_pmi_status(self):
        self.pmi_ai_s = None
        self.pmi_telem = None
        self.pmi_path = []

    def reset_robots(self):
        self.robots = []

    """ EVENT """

    """ Update score """
    @Service.event('score')
    def get_score(self, value=0):
        if self.match_status != 'started':
            return
        self.score += int(value)
        print('[MATCH] score is now: %d' % self.score)

    """ PAL """
    @Service.event
    def pal_telemetry(self, status, telemetry):
        self.pal_watchdog.reset()
        if status != 'failed':
            self.pal_telem = telemetry
        else:
            self.pal_telem = None

    @Service.event
    def pal_ai_status(self, status, path):
        self.pal_watchdog.reset()
        self.pal_ai_s = status
        self.pal_path = path

    """ PMI """
    @Service.event
    def pmi_telemetry(self, status, telemetry):
        self.pmi_watchdog.reset()
        if status != 'failed':
            self.pmi_telem = telemetry
        else:
            self.pmi_telem = None

    @Service.event
    def pmi_ai_status(self, status):
        self.pmi_watchdog.reset()
        self.pmi_ai_s = status

    """ Oppenents """
    @Service.event
    def opponents(self, robots):
      self.robots = robots
      self.robots_watchdog.reset()

    """ Tirette """
    @Service.event('tirette')
    def match_start(self, name, id, value):
        if self.match_status != 'unstarted' or self.color is None:
            return

        self.publish('match_start')
        self.timer.start()
        self.match_status = 'started'
        print('[MATCH] Match start')
        self.match_time_thread.start()

    """ ACTION """

    """ Reset match """
    @Service.action
    def reset_match(self, color=None):
        if self.match_status == 'started':
            print("[MATCH] Can't reset match, match is running")
            return False

        print('[MATCH] Reset match')
        self.match_status = 'unstarted'
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

        if self.match_status == 'started':
            print("[MATCH] Can't set color, match is running")

        self.color = color

        self.publish('match_color', color=self.color)
        return True

    """ Get match """
    @Service.action
    def get_match(self):
        match = {}

        match['status'] = self.match_status
        match['color'] = self.color
        match['robots'] = self.robots
        match['score'] = self.score
        match['time'] = self.match_time

        match['pal_ai_status'] = self.pal_ai_s
        match['pal_telemetry'] = self.pal_telem

        match['pmi_ai_status'] = self.pmi_ai_s
        match['pmi_telemetry'] = self.pmi_telem

        return match

    """ End match """
    @Service.action
    def match_end(self):
        self.publish('match_end')
        self.match_status = 'ended'
        print('[MATCH] Match End')


    """ THREAD """

    """ Match status thread """
    #@Service.thread
    def match_status(self):
      while True:
        #Usefull ?
        #self.publish('match_status', match=self.get_match())

        # Update PAL LCD
        # TODO: Use LCD on exp
        try:
            pass
        except:
            pass
        sleep(self.refresh)

    """ Interface thread """
    @Service.thread
    def launch_interface(self):
        if self.interface_enabled:
            MatchInterface(self)

    def match_time_loop(self):
        while self.match_status == 'started':
            self.match_time += 1
            sleep(1)

def main():
    #waitBeacon()
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
