import os

from evolutek.lib.interface import Interface
from evolutek.lib.settings import SIMULATION
from evolutek.lib.watchdog import Watchdog

if SIMULATION:
	from evolutek.simulation.simulator import read_config

from tkinter import Button, Canvas, Label, ttk


# TODO: clean

class IAInterface(Interface):

	def __init__(self, ia):
		super().__init__('IA', 3)

		self.init_robot('pal')
		self.ia = ia

		self.match_status = None
		self.client.add_subscribe_cb('match_status', self.match_status_handler)
		self.match_status_watchdog = Watchdog(3,
		                                      self.reset_match_status)  # float(match_config['refresh']) * 2, self.reset_match_status)

		if SIMULATION:
			self.init_simulation()

		self.window.after(self.interface_refresh, self.update_interface)
		print('[IA NTERFACE] Window looping')
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

	def action_color(self, event):
		self.cs.match.set_color(self.select_color.get())

	def action_strategy(self, event):
		self.ia.strategy = self.select_strategy.get()
		self.ia.goals.reset(self.select_strategy.get())

	def shutdown(self):
		return os.system("poweroff")

	# TODO:
	# faire la recalibration
	def event_recalibration(self):
		print(self.robots['pal'])
		print("\n\n\n")

	# Init match interface
	def init_interface(self):

		# select color
		list_color = [self.color2, self.color1]
		self.select_color = ttk.Combobox(self.window, values=list_color)
		self.select_color.current(0)
		self.select_color.grid(row=6, column=0)
		self.select_color.bind("<<ComboboxSelected>>", self.action_color)

		# Close button
		self.close_button = Button(self.window, text='Close', command=self.close)
		self.close_button.grid(row=9, column=0)

		self.shutdown_button = Button(self.window, text='Éteindre', command=self.close)
		self.shutdown_button.grid(row=10, column=0)

		self.recalibration_button = Button(self.window, text='Recalibration', command=self.event_recalibration)
		self.recalibration_button.grid(row=11, column=0)

		# Reset Button
		self.reset_button = Button(self.window, text='Reset Match', command=self.reset_match)
		self.reset_button.grid(row=8, column=0)

		# select strategy
		list_strategy = [self.ia.goals().current_strategy]
		self.select_strategy = ttk.Combobox(self.window, values=list_strategy)
		self.select_strategy.current(self.ia.goals.current_strategy())
		self.select_strategy.bind("<<ComboboxSelected>>", self.action_strategy)
		self.select_strategy.grid(row=7, column=0)

		# Map
		self.canvas = Canvas(self.window, width=3000 * self.interface_ratio, height=2000 * self.interface_ratio)
		self.canvas.grid(row=6, column=1, columnspan=4, rowspan=11)

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

		self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

	def update_interface(self):
		print(self.get_robot_status('pal'))
		self.canvas.delete('all')
		self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)
		self.bau_status_label.config(text='%s' % ' Bau Status: mise' if self.ia.bau.read == 0 else 'Bau Status: enlever')
		#self.print_robot({"y": 100, "x": 630, "theta": 6.28}, self.robots["pal"]['size'], self.robots["pal"]['color'])
		self.print_robot(self.robots['pal']["telemetry"], self.robots["pal"]['size'], self.robots["pal"]['color'])
		if self.match_status is not None:

			self.color_label.config(text="Color: %s" % self.match_status['color'], fg=self.match_status['color'])
			self.score_label.config(text="Score: %d" % self.match_status['score'])
			self.match_status_label.config(text="Match status: %s" % self.match_status['status'])
			self.match_time_label.config(text="Match time: %d" % self.match_status['time'])

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


class Ia():
	def __init__(self):
		self.strategy = ""

	class bau:
		@property
		def read(self):
			return 0

	class goals:

		def __init__(self):
			self.strategies = ["bonjour", "strategy1", "lolo", "bonjour"]

def main():
	IAInterface(Ia())


if __name__ == "__main__":
	main()
