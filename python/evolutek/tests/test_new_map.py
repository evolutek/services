from evolutek.lib.map.debug_new_map import Interface
from evolutek.lib.map.new_map import Map, ObstacleType, parse_obstacle_file
from evolutek.lib.map.point import Point

from threading import Thread, Event
from time import sleep, time

class Test_Map:

    def __init__(self):

        self.robot_size = 150

        # Tested map
        self.map = Map(3000, 2000, self.robot_size)
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map.add_obstacles(fixed_obstacles)
        self.map.add_obstacles(self.color_obstacles, False, type=ObstacleType.color)

        self.color = 'violet'
        self.path = []

        self.compute_path = Event()

        self.map.add_rectangle_obstacle(Point(1000, 1400), Point(2000, 1600))

        # Threads
        Thread(target=Interface, args=[self.map, self]).start()
        Thread(target=self.fake_robot).start()
        Thread(target=self.loop_path).start()

    def loop_path(self):
        while True:
            print('[TEST_MAP] Update path')
            self.compute_path.wait()
            start = time()
            self.path = self.map.get_path(Point(250, 500), Point(1200, 2300))
            end = time()
            self.compute_path.clear()
            print('Path compute in: ' + str(end-start))

    def fake_robot(self):
        robot = {'x': 750, 'y': 2029}
        ascending = True

        while True:
            while self.compute_path.isSet():
                sleep(0.01)
            #print('[TEST_MAP] Update Fake Robot')
            if ascending:
                robot['y'] += 50
                if robot['y'] > 2400:
                    robot['y'] = 2399
                    ascending = False
            else:
                robot['y'] -= 50
                if robot['y'] < 299:
                    robot['y'] = 201
                    ascending = True

            pos = Point(dict=robot)
            obstacle = self.map.add_octogon_obstacle(pos, self.robot_size, tag='fake', type=ObstacleType.robot)
            self.compute_path.set()

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
