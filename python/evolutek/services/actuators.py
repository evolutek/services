import cellaserv.proxy

import mraa

from cellaserv.service import Service
from time import sleep

class actuators(Service):

	def __init__(self):
		super().__init__(identification=str('pal'))
		self.robot = cellaserv.proxy.CellaservProxy()
		for n in [10, 11]:
			self.robot.ax[str(n)].mode_joint()
		print("Actuators : Init Done")

	@Service.action
	def open_door(self):
		self.robot.ax["1"].move(goal = 700)
		self.robot.ax["2"].move(goal = 200)

def main():
	actuators_pal = actuators()
	Service.loop()

if __name__ == "__main__":
	main()
