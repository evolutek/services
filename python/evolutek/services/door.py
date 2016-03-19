import cellaserv.proxy

forom cellaserv.service import Service

class Door(Service):

	def __init__(self, ax):
		super().__init__(identification=str(trigger))
		self.ax = ax

	@Service.action
	def open(self):
		robot.ax["1"].move(goal = 200)
		robot.ax["2"].move(goal = 900)

	@Service.action
	def demi_close(self):
		robot.ax["1"].move(goal = 400)
		robot.ax["2"].move(goal = 700)

	@Service.action
	def close(self):
		robot.ax["1"].move(goal = 900)
		robot.ax["2"].move(goal = 300)

def main():
	robot = cellaserv.proxy.CellaservProxy()
	axs = [Ax(ax=i) for i in [1,2]]
	robot.ax[1].mode_joint()
	robot.ax[2].mode_joint()
	robot.ax["1"].move(goal = 200)
	robot.ax["2"].move(goal = 900)

if __name__ == "__main__":
	main()