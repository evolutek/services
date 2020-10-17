from sys import argv
from time import sleep
from math import pi
from cellaserv.proxy import CellaservProxy
from evolutek.lib.robot import Robot, Point

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
		list_goals = [self.goals_4]
		self.robot.recalibration(init=True)
		for goal in list_goals:
			goal()
			self.tidy_actuators()
			input("please replace the robot for the next goals:\n press enter if you finish")
			self.robot.recalibration(init=True)
		return True

	def tidy_actuators(self):
		self.cs.actuators[ROBOT].right_cup_holder_close()
		self.cs.actuators[ROBOT].left_cup_holder_close()
		self.cs.actuators[ROBOT].left_arm_close()
		self.cs.actuators[ROBOT].right_arm_close()

	def goals_1(self):
		print("[GOALS 1] start")
		self.robot.go_home(Point(x=640, y=120), pi/2)
		self.cs.actuators[ROBOT].pump_get(4, 'red')
		self.robot.goto(640, 250)
		self.robot.goth(pi)
		self.cs.actuators[ROBOT].pump_get(2, 'red')
		self.robot.move_trsl_block(160, 400,400,500, True)
		print("[GOALS 1] end")

	def goals_2(self):
		print("[GOALS 2] start")
		self.robot.goto(200, 250)
		self.robot.goth(0)
		self.cs.actuators[ROBOT].right_cup_holder_open()
		self.cs.actuators[ROBOT].left_cup_holder_open()
		self.robot.tm.move_trsl(70, 100, 100, 250, 1)
		self.robot.tm.move_trsl(70, 100, 100, 250, 0)
		print("[GOALS 2] end")
		self.cs.actuators[ROBOT].right_cup_holder_close()
		self.cs.actuators[ROBOT].left_cup_holder_close()
	# 220 880
	# 110 

	def goals_4(self):
		print("[GOALS 4] start")
		self.robot.goto(220, 880)
		self.robot.goth(0)
		self.cs.actuators[ROBOT].right_cup_holder_open()
		self.cs.actuators[ROBOT].left_cup_holder_open()
		self.cs.actuators[ROBOT].pump_get(5, 'green')
		self.cs.actuators[ROBOT].pump_get(6, 'red')
		self.cs.actuators[ROBOT].pump_get(7, 'green')
		self.cs.actuators[ROBOT].pump_get(8, 'red')
		self.robot.tm.move_trsl(280, 100, 100, 250, 0)
		sleep(2)
		self.cs.actuators[ROBOT].left_cup_holder_close()
		self.cs.actuators[ROBOT].right_cup_holder_close()
		sleep(2)
		self.robot.tm.move_trsl(280, 100, 100, 500, 1)
		print("[GOALS 4] end")
		

	def goals_8(self, ):
		print("[GOALS 8] start")
		sleep(2)
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
		self.robot.tm.move_trsl(90, 100, 100, 250, 0)
		sleep(2)
		self.robot.tm.move_trsl(90, 100, 100, 500, 1)

		self.cs.actuators[ROBOT].left_cup_holder_close()
		self.cs.actuators[ROBOT].right_cup_holder_close()
		print("[GOALS 8] end")

	def goals_9(self):
		print("[GOALS 9] start")
		self.robot.goto(1830, 200)
		self.robot.goth(pi / 2)
		self.robot.recalibration_block(sens=0)
		self.push_windsocks(4)
		print("[GOALS 9] end")

	def push_windsocks(self, ax):

		# self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=512)

		self.cs.actuators[ROBOT].left_arm_open() if ax == 3 else cs.actuators[ROBOT].right_arm_open()

		# TODO config
		self.robot.tm.set_delta_max_rot(0.5)
		self.robot.tm.set_delta_max_trsl(300)

		self.robot.tm.move_trsl(dest=650, acc=800, dec=800, maxspeed=1000, sens=1)

		sleep(2)

		# self.cs.ax["%s-%d" % (ROBOT, ax)].move(goal=820 if ax != 3 else 210)
		self.cs.actuators[ROBOT].left_arm_close() if ax == 3 else cs.actuators[ROBOT].right_arm_close()

		self.robot.tm.set_delta_max_rot(0.2)
		self.robot.tm.set_delta_max_trsl(100)

		self.robot.move_trsl_block(100, 400, 400, 500, 0)


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
