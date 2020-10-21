import os

from evolutek.lib.interface import Interface
from evolutek.lib.settings import SIMULATION
from evolutek.lib.watchdog import Watchdog
if SIMULATION:
	from evolutek.simulation.simulator import read_config

from tkinter import Button, Canvas, Label, ttk


# TODO: clean

class IAInterface(Interface):

	def __init__(self, ai):
		super().__init__('Ai interface', 3)

		self.ia = ai
		self.init_robot("pal")

		self.match_status = None
		self.client.add_subscribe_cb('match_status', self.match_status_handler)
		self.match_status_watchdog = Watchdog(3, self.reset_match_status)  # float(match_config['refresh']) * 2, self.reset_match_status)
		if SIMULATION:
			self.init_simulation()

		self.window.after(self.interface_refresh, self.update_interface)
		print('[AI NTERFACE] Window looping')
		self.window.mainloop()

	def init_simulation(self):
		enemies = read_config('enemies')

		if enemies is None:
			return

		for enemy, config in enemies['robots'].items():
			self.robots[enemy] = {'telemetry': None, 'size': config['config']['robot_size_y'], 'color': 'red'}
			self.client.add_subscribe_cb(enemy + '_telemetry', self.telemetry_handler)

	def match_status_handler(self, status):
		self.match_status_watchdog.reset()
		print(status, end="\n")
		self.match_status = status

	def reset_match_status(self):
		self.match_status = None

	def reset_match(self):
		try:
			self.cs.match.reset_match()
		except Exception as e:
			print('[IA INTERFACE] Failed to reset match : %s' % str(e))

	def action_color(self):
		if self.match_status["color"] == self.ia.robot.color1:
			self.cs.match.set_color(self.color2)
		else:
			self.cs.match.set_color(self.ia.robot.color1)

	def action_strategy(self, event):
		self.ia.goals.reset(self.select_strategy.get())

	def shutdown(self):
		os.system("poweroff")

	def event_recalibration(self):
		self.ia.set_recalibration(True)

	def event_set_pos(self):
		self.ia.set_recalibration(False)
	# Init match interface
	def init_interface(self):

		# button color
		self.color_button = Button(self.window, text='Change color', command=self.action_color)
		self.color_button.grid(row=7, column=0)

		# Close button
		self.close_button = Button(self.window, text='Close', command=self.close)
		self.close_button.grid(row=9, column=0)

		# Reset Button
		self.reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
		self.reset_button.grid(row=8, column=0)

		self.shutdown_button = Button(self.window, text='shutdown', command=self.close)
		self.shutdown_button.grid(row=10, column=0)

		self.recalibration_button = Button(self.window, text='Recalibration', command=self.event_recalibration)
		self.recalibration_button.grid(row=11, column=0)

		self.homologation_button = Button(self.window, text='Homologation', command=self.event_homologation)
		self.homologation_button.grid(row=12, column=0)

		# Reset Button
		self.resset_pos = Button(self.window, text='Reset position', command=self.event_set_pos)
		self.resset_pos.grid(row=13, column=0)

		# select strategy
		list_strategy = ["bonjour", "bonjour"]
		self.select_strategy = ttk.Combobox(self.window, values=list_strategy)
		self.select_strategy.current(0)
		self.select_strategy.bind("<<ComboboxSelected>>", self.action_strategy)
		self.select_strategy.grid(row=6, column=0)

		# Map
		self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height=2000 * self.interface_ratio)
		self.canvas.grid(row=6, column=1, columnspan=4, rowspan=14)

		# Color
		self.color_label = Label(self.window)
		self.color_label.grid(row=0, column=1)
		self.color_label.config(font=('Arial', 12))

		# Score
		self.score_label = Label(self.window)
		self.score_label.grid(row=0, column=0)
		self.score_label.config(font=('Arial', 16))

		# Match status
		self.match_status_label = Label(self.window)
		self.match_status_label.grid(row=0, column=2)
		self.match_status_label.config(font=('Arial', 12))

		# BAU STATUS
		self.bau_status_label = Label(self.window)
		self.bau_status_label.grid(row=0, column=3)
		self.bau_status_label.config(font=('Arial', 12))

		# Match time
		self.match_time_label = Label(self.window)
		self.match_time_label.grid(row=0, column=4)
		self.match_time_label.config(font=('Arial', 12))

		self.ia_status = Label(self.window)
		self.ia_status.grid(row=0, column=5)
		self.ia_status.config(font=('Arial', 12))

		self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

	def update_interface(self):
		self.canvas.delete('all')
		self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)
		self.bau_status_label.config(text='%s' % ' Bau Status: mise' if self.ia.bau.read == 0 else 'Bau Status: enlever')
		self.ia_status.config(text='État ia: %s' % str(self.ia.fsm.running))

		if self.match_status is not None:

			self.color_label.config(text="Color: %s" % self.match_status['color'], fg=self.match_status['color'])
			self.score_label.config(text="Score: %d" % self.match_status['score'])
			self.match_status_label.config(text="Match status: %s" % self.match_status['status'])
			self.match_time_label.config(text="Match time: %d" % self.match_status['time'])
			self.color_button.config(bg=self.match_status["color"])

		else:

			self.color_label.config(text="Color: %s" % 'M.C')
			self.score_label.config(text="Score: %s" % 'M.C')
			self.match_status_label.config(text="Match status: %s" % 'M.C')
			self.match_time_label.config(text="Match time: %s" % 'M.C')

		self.tmp.clear()
		for robot in self.robots:
			if robot in ['pal', 'pmi']:
				self.print_robot_image(robot, self.robots[robot]['telemetry'])
			else:
				self.print_robot(*self.robots[robot].values())

		self.print_path(self.paths['pal'], 'yellow', 'violet')

		self.window.after(self.interface_refresh, self.update_interface)


class Ai:
	def __init__(self):
		self.fsm = Ai.Fsm()
		self.goals = Ai.Goals()

	class robot:
		color1 = 'blue'

	class bau:
		def __init__(self):
			pass

		@staticmethod
		def read():
			return True

	class Fsm:

		def __init__(self):
			self.running = "Bonjour"

	class Goals:
		def __init__(self):
			self.strategies = ["Bonjour", "Geooi", "pfdjfmd"]
def main():
	IAInterface(Ai())


if __name__ == "__main__":
	main()
