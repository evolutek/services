from threading import Timer

class Watchdog:

	def __init__(self, timeout, userHandler=None, userArgs=None):
		self.timeout = timeout
		self.handler = userHandler if userHandler is not None\
			else self.defaultHandler

		self.args = userArgs if userArgs is not None else []
		self.timer = Timer(self.timeout, self.handler, self.args)

	def reset(self):
		#print("reset watchdog timer")
		self.timer.cancel()
		self.timer = Timer(self.timeout, self.handler, self.args)
		self.timer.start()

	def stop(self):
		#print("stop watchdog timer")
		self.timer.cancel()

	def defaultHandler(self):
		raise self
