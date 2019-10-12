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
        Thread(target=self.fake_robot).start()
        sleep(0.5)
        Thread(target=self.loop_path).start()

    def loop_path(self):
        while True:
          self.path = self.pathfinding.get_path(Point(250, 500), Point(1200, 2300))
          sleep(0.1)

    def fake_robot(self):
        robot = {'x': 750, 'y': 500}
        ascending = True
        while True:
            if ascending:
                robot['y'] += 10
                if robot['y'] > 1750:
                    robot['y'] = 1749
                    ascending = False
            else:
                robot['y'] -= 10
                if robot['y'] < 500:
                    robot['y'] = 501
                    ascending = True

            self.map.remove_obstacle('fake')
            #self.map.add_circle_obstacle(Point.from_dict(robot), self.robot_size, tag='fake', type=ObstacleType.robot)
            pos = Point.from_dict(robot)
            #print(pos)
            obstacle = self.map.add_rectangle_obstacle(Point(pos.x - self.robot_size, pos.y - self.robot_size), Point(pos.x + self.robot_size, pos.y + self.robot_size), tag='fake', type=ObstacleType.robot)
            #self.map.replace_obstacle('fake', obstacle)
            sleep(0.1)

if __name__ == "__main__":
    print('[TEST_MAP] Starting test')
    test_map = Test_Map()
