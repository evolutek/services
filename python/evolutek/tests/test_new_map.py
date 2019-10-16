from evolutek.lib.map.debug_new_map import Interface
from evolutek.lib.map.new_map import Map, ObstacleType, parse_obstacle_file
from evolutek.lib.map.point import Point

from threading import Thread
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

        self.map.add_rectangle_obstacle(Point(1000, 1400), Point(2000, 1600))

        # Threads
        Thread(target=Interface, args=[self.map, self]).start()
        Thread(target=self.fake_robot).start()
        sleep(0.5)
        Thread(target=self.loop_path).start()

    def loop_path(self):
        while True:
            #print('[TEST_MAP] Update path')
            start = time()
            self.path = self.map.get_path(Point(250, 500), Point(1200, 2300))
            end = time()
            print('Path compute in: ' + str(end-start))
            sleep(0.3)

    def fake_robot(self):
        robot = {'x': 750, 'y': 2129}
        ascending = True
        while True:
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

            #self.map.add_circle_obstacle(Point.from_dict(robot), self.robot_size, tag='fake', type=ObstacleType.robot)
            pos = Point(dict=robot)
            obstacle = self.map.add_octogon_obstacle(pos, self.robot_size, tag='fake', type=ObstacleType.robot)
            #self.map.replace_obstacle('fake', obstacle)
            sleep(0.3)

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
