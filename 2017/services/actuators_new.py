import cellaserv.proxy

from cellaserv.service import Service
from time import sleep

@Service.require("ax", "1")
class actuators(Service):

	def __init__(self, act):
		super().__init__(identification=str(act))
		self.robot = cellaserv.proxy.CellaservProxy()
		self.minimal_delay = 2
		for n in [1,2,3,4,5]:
			self.robot.ax[str(n)].mode_joint()
		print("Actuators : Init Done")

	@Service.action
	def launch_rocket(self):
		self.robot.ax["3"].move(goal = 1000)

def main():
	actuators_pal = actuators("pal")
	Service.loop()

if __name__ == "__main__":
	main()
