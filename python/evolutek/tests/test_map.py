from evolutek.lib.map.debug_map import Interface
from evolutek.lib.map.map import Map
from evolutek.lib.map.obstacle import ObstacleType, parse_obstacle_file
from evolutek.lib.map.pathfinding import Pathfinding
from evolutek.lib.map.point import Point

from threading import Thread
from time import sleep

class Test_Map:

    def __init__(self):

        self.robot_size = 150

        # Tested map
        self.map = Map(3000, 2000, 25, self.robot_size)
        fixed_obstacles, self.color_obstacles = parse_obstacle_file('/etc/conf.d/obstacles.json')
        self.map.add_obstacles(fixed_obstacles)
        self.map.add_obstacles(self.color_obstacles, False, type=ObstacleType.color)

        #Tested Pathfinding
        self.pathfinding = Pathfinding(self.map)
        self.path = []

        # Threads
        Thread(target=Interface, args=[self.map, self]).start()
        Thread(target=self.loop_path).start()
        Thread(target=self.fake_robot).start()

    def loop_path(self):
        while True:
          self.path = self.pathfinding.get_path(Point(750, 250), Point(750, 2300))
          sleep(0.05)

    def fake_robot(self):
        robot = {'x': 750, 'y': 750}
        ascending = True
        while True:
            if ascending:
                robot['y'] += 10
                if robot['y'] > 1750:
                    robot['y'] = 1749
                    ascending = False
            else:
                robot['y'] -= 10
                if robot['y'] < 750:
                    robot['y'] = 751
                    ascending = True

            self.map.remove_obstacle('fake')
            self.map.add_circle_obstacle(Point.from_dict(robot), self.robot_size, tag='fake', type=ObstacleType.robot)
            sleep(0.05)

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
