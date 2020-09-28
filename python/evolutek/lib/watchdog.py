from threading import Timer

# Watchdog class
# timeout: Timeout of the timer of the watchdog
# userHandler: Callback to call at the end of the timer
# userArgs: Args for the callback
class Watchdog:

	def __init__(self, timeout, userHandler=None, userArgs=None):
		self.timeout = timeout
		self.handler = userHandler if userHandler is not None\
			else self.defaultHandler

		self.args = userArgs if userArgs is not None else []
		self.timer = Timer(self.timeout, self.handler, self.args)

	# Reset the timer of the watchdog
	def reset(self):
		#print("reset watchdog timer")
		self.timer.cancel()
		self.timer = Timer(self.timeout, self.handler, self.args)
		self.timer.start()

	# Stop the timer
	def stop(self):
		#print("stop watchdog timer")
		self.timer.cancel()

	# Default callback
	def defaultHandler(self):
		raise self
