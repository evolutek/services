from sys import argv
from time import sleep
from math import pi

from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot

cs = CellaservProxy()
ROBOT = None
robot = None


def move_ax(id, pos):
	cs.ax["%s-%d" % (ROBOT, id)].move(goal=pos)


class TestGoals:

	def __init__(self, cs=None, robot=None):
		self.cs = cs
		self.robot = robot

		if self.robot is None:
			print("[TEST] robot not initialized")
		elif self.cs:
			print("[TEST] cs not initialized")
		self.run()

	def run(self):
		print("[TEST] TEST Goals 8: ")
		self.goals_8()
		print("going starting pos")
		self.robot.goto(150, 200)
		self.robot.goth(0)

		return True

	def goals_8(self,):
		print("[GOALS 8] start")
		sleep(2)

		self.robot.recalibration(init=True)
		self.robot.goto(1800, 200)
		self.robot.goth(pi)
		self.robot.recalibration(y=False, init=False, side_x=(False, True))
		self.robot.goto(1616, 200)
		self.robot.goth(pi / 2)
		self.cs.actuators[ROBOT].right_cup_holder_open()
		self.cs.actuators[ROBOT].left_cup_holder_open()
		self.cs.actuators[ROBOT].pump_get(5, 'green')
		self.cs.actuators[ROBOT].pump_get(6, 'red')
		self.cs.actuators[ROBOT].pump_get(7, 'green')
		self.cs.actuators[ROBOT].pump_get(8, 'red')
		self.robot.tm.move_trsl(200, 100, 100, 250, 0)
		sleep(2)
		self.robot.tm.move_trsl(200, 100, 100, 500, 1)

		self.cs.actuators[ROBOT].left_cup_holder_close()
		self.cs.actuators[ROBOT].right_cup_holder_close()
		print("[GOALS 8] end")

def main():
	selected_robot = argv[1]
	if not selected_robot in ['pal', 'pmi']:
		print("select a valid robot")
		return

	global ROBOT
	ROBOT = selected_robot
	global robot
	robot = Robot(selected_robot)
	TestGoals(cs, robot)

if __name__ == "__main__":
	main()