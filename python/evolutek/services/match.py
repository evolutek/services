from cellaserv.proxy import CellaservProxy
from cellaserv.service import Service

import cv2 as cv
from enum import Enum
from threading import Timer, Thread
from time import localtime, sleep, time, strftime

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
        self.stop_delay = int(match_config['stop_delay'])
        self.match_duration = int(match_config['duration'])

        # Match Status
        self.match_status = MatchStatus.unstarted
        self.color = None
        self.set_color(self.color1)
        self.score = 0
        self.start_time = 0

        print('[MATCH] Match ready')

    """ EVENT """

    """ Update score """
    @Service.event('score')
    def add_score(self, value=0):
        self.score += int(value)
        print('[MATCH] score is now: %d' % self.score)

    def record_match(self, match_duration=100):
        # Define the duration (in seconds) of the video capture here
        DIM = (1280, 720)
        capture_duration = int(match_duration + 5)
        cap = cv.VideoCapture(0)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, DIM[0])
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, DIM[1])

        ts = strftime("%Y-%m-%d_%H-%M-%S", localtime())
        # Define the codec and create VideoWriter object
        fourcc = cv.VideoWriter_fourcc(*'XVID')
        video_title = f'/home/pi/{ts}_match.avi'
        out = cv.VideoWriter(video_title, fourcc, 20.0, DIM)
        start_time = time()
        while int(time() - start_time) < capture_duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        # Release everything if job is finished
        cap.release()
        out.release()
        cv.destroyAllWindows()

    """ Tirette """
    @Service.event('tirette')
    def match_start(self, name='', id=0, value=0):

        if self.match_status != MatchStatus.unstarted or self.color is None:
            return

        self.start_time = time()

        self.publish('match_start')
        Thread(target=self.record_match, args=[self.match_duration]).start()
        match_timer = Timer(self.match_duration, self.match_end)
        match_timer.start()
        self.match_status = MatchStatus.started
        self.score += 5
        print('[MATCH] Match start')

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

    def _set_match_end(self):
        self.match_status = MatchStatus.ended
        print('[MATCH] Match End')

    # FIXME : FIX THIS
    def around(self, robot, x, y, rx, ry):
        if self.color == self.color2: y = 2000 - y
        pos = None
        try:
            pos = self.cs.trajman[robot].get_position()
        except Exception as e:
            print('[MATCH] Failed to contact trajman/%s: %s' % (robot, str(e)))
            return False
        if pos['x'] > x+rx or pos['x'] < x-rx: return False
        if pos['y'] > y+ry or pos['y'] < y-ry: return False
        return True

    def check_end_positions(self):
        pal_around = self.around('pal', 1650, 450, 50, 50)
        pmi_around = self.around('pmi', 2100, 450, 50, 50)

        # Go back action
        if pal_around and pmi_around:
            self.score += 15

        # Disguise action
        if pal_around or pmi_around:
            self.score += 5

    """ End match """
    @Service.action
    def match_end(self):
        print('[MATCH] Call for match end')
        self.check_end_positions()
        self.publish('match_end')
        Timer(self.stop_delay, self._set_match_end).start()

def main():
    match = Match()
    match.run()

if __name__ == '__main__':
    main()
