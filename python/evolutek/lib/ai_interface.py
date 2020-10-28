#! /usr/bin/python3

import os

from evolutek.lib.settings import ROBOT
from cellaserv.service import Service
import json
from evolutek.lib.interface import Interface
from evolutek.lib.settings import SIMULATION
from evolutek.lib.watchdog import Watchdog
if SIMULATION:
	from evolutek.simulation.simulator import read_config

from sys import argv
from tkinter import Button, Canvas, Label, ttk


# TODO: clean

class AIInterface(Interface):

	def __init__(self):

		super().__init__('Ai interface', 3)
		self.init_robot(ROBOT)
		self.match_status = None
		self.bau_status = None
		self.states_ai = None
		self.client.add_subscribe_cb(ROBOT + '_infos_interfaces', self.infos_ai)
		self.match_status_watchdog = Watchdog(3, self.reset_match_status)  # float(match_config['refresh']) * 2, self.reset_match_status)
		if SIMULATION:
			self.init_simulation()

		self.window.after(500, self.update_interface)
		print('[AI NTERFACE] Window looping')
		self.window.mainloop()

	def infos_ai(self, states_ai, bau_status):
		self.bau_status = bau_status
		self.states_ai = states_ai

	def init_simulation(self):
		enemies = read_config('enemies')

		if enemies is None:
			return

		for enemy, config in enemies['robots'].items():
			self.robots[enemy] = {'telemetry': None, 'size': config['config']['robot_size_y'], 'color': 'red'}
			self.client.add_subscribe_cb(enemy + '_telemetry', self.telemetry_handler)
	#
	# def match_status_handler(self, status):
	# 	self.match_status_watchdog.reset()
	# 	print(status, end="\n")
	# 	self.match_status = status

	def reset_match_status(self):
	    self.match_status = None

	def reset_match(self):
		try:
			self.cs.match.reset_match()
		except Exception as e:
			print('[IA INTERFACE] Failed to reset match : %s' % str(e))

	def action_color(self):
		if self.cs.match.get_color() == self.color1:
			self.cs.match.set_color(self.color2)
		else:
			self.cs.match.set_color(self.color1)

	def action_strategy(self):
		self.client.publish(ROBOT + "_strategy", strategy=self.select_strategy.get(), ai=ROBOT)

	def shutdown(self):
		os.system("sudo shutdown now")
		print('Gros je me casse')

	def event_recalibration(self):
		self.client.publish(ROBOT + "_recalibration")
		self.client.publish(ROBOT + "_reset")

	def event_set_pos(self):
		self.client.publish(ROBOT + "_reset")

	def parse_strategy(self, file):
		data = None
		try:
			with open(file, 'r') as goals_file:
				data = goals_file.read()
		except Exception as e:
			print('[GOALS] Failed to read file: %s' % str(e))
			return False

		goals = json.loads(data)
		list_robot = []

		for i in goals["strategies"]:
			if ROBOT in i["available"]:
				list_robot.append(i)
		return list_robot

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

		self.shutdown_button = Button(self.window, text='shutdown', command=self.shutdown)
		self.shutdown_button.grid(row=10, column=0)

		self.recalibration_button = Button(self.window, text='Recalibration', command=self.event_recalibration)
		self.recalibration_button.grid(row=11, column=0)

		# Reset Button
		self.resset_pos = Button(self.window, text='Reset position', command=self.event_set_pos)
		self.resset_pos.grid(row=13, column=0)

		# select strategy
		list_strategy = self.parse_strategy(file='/etc/conf.d/strategies.json')
		self.select_strategy = ttk.Combobox(self.window, values=list_strategy[0])
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
		self.score_label.config(font=('Arial', 25))

		# Match status
		self.match_status_label = Label(self.window)
		self.match_status_label.grid(row=0, column=2)
		self.match_status_label.config(font=('Arial', 12))

		# # BAU STATUS
		#self.bau_status_label = Label(self.window)
		#self.bau_status_label.grid(row=0, column=3)
		#self.bau_status_label.config(font=('Arial', 12))

		# Match time
		self.match_time_label = Label(self.window)
		self.match_time_label.grid(row=0, column=4)
		self.match_time_label.config(font=('Arial', 12))

		self.canvas.create_image(1500 * self.interface_ratio, 1000 * self.interface_ratio, image=self.map)

	def update_interface(self):
		self.canvas.delete('all')
		self.canvas.create_image((3000 * self.interface_ratio) / 2, (2000 * self.interface_ratio) / 2, image=self.map)
		#self.bau_status_label.config(text='%s' % ' Bau Status: ON' if self.bau_status else 'Bau Status: OFF')

		if self.cs.match.get_status() is not None:
			self.color_label.config(text="Color: %s" % self.cs.match.get_color(), fg=self.cs.match.get_status()['color'])
			self.score_label.config(text="Score: %d" % self.cs.match.get_status()['score'])
			self.match_status_label.config(text="Match status: %s" % self.cs.match.get_status()['status'])
			self.match_time_label.config(text="Match time: %d" % self.cs.match.get_status()['time'])
			self.color_button.config(bg=self.cs.match.get_color())

		else:
			print("[FIX] match not running or problem with this")

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

		self.print_path(self.paths[ROBOT], 'yellow', 'violet')

		self.window.after(500, self.update_interface)

def main():
	if len(argv) > 1:
		global ROBOT
		ROBOT = argv[1]
	AIInterface()


if __name__ == "__main__":
	main()
