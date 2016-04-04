import cellaserv.proxy

from cellaserv.service import Service
from time import sleep

class Actuators_pal(Service):

	def __init__(self, ax):
		super().__init__(identification=str(trigger))
		self.ax = ax
		self.robot = cellaserv.proxy.CellaservProxy()
		self.minimal_delay = 0.8
		for n in [1,2,3,4,5]:
            self.cs.ax[str(n)].mode_joint()
        self.robot.ax["1"].move(goal = 200)
		self.robot.ax["2"].move(goal = 700)
		self.robot.ax["3"].move(goal = 500)
		self.robot.ax["4"].move(goal = 640)
		self.robot.ax["5"].move(goal = 200)
        print("Actuators : Init Done")


	@Service.action
	def open_door(self):
		self.robot.ax["1"].move(goal = 700)
		self.robot.ax["2"].move(goal = 200)

	@Service.action
	def close_door(self):
		self.robot.ax["1"].move(goal = 200)
		self.robot.ax["2"].move(goal = 700)

	@Service.action
	def open_umbrella(self):
		self.robot.ax["3"].move(goal = 1000)

	@Service.action
	def close_umbrella(self):
		self.robot.ax["3"].move(goal = 500)

	@Service.action
	def open_arm_left(self):
		self.robot.ax["4"].move(goal = 340)
		time.sleep(minimal_delay)
		self.robot.ax["5"].move(goal = 800)
		time.sleep(minimal_delay)
		self.robot.ax["4"].move(goal = 40)

	@Service.action
	def open_arm_right(self):
		self.robot.ax["4"].move(goal = 640)
		time.sleep(self.minimal_delay)
		self.robot.ax["5"].move(goal = 800)

	@Service.action
	def demi_open_arm(self):
		self.robot.ax["5"].move(goal = 650)

	@Service.action
	def close_arm(self):
		self.robot.ax["5"].move(goal = 800)
		time.sleep(self.minimal_delay)
		self.robot.ax["4"].move(goal = 640)

def main():
	Actuators = Actuators_pal()
	Service.loop()
	
if __name__ == "__main__":
	main()