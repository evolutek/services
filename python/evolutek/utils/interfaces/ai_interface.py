#! /usr/bin/python3

import os

from evolutek.lib.settings import ROBOT
from cellaserv.service import Service
import json
from tkinter import *
from evolutek.lib.settings import SIMULATION

if SIMULATION:
	from evolutek.simulation.simulator import read_config

from sys import argv
from tkinter import Button, Canvas, Label, ttk
from evolutek.lib.interface import Interface


class IFRAME(Frame):
	def __init__(self, container, border=0):
		self.parent = container
		self.ai = container.ai
		super().__init__(self.parent.window, bd=border)

	def update_interface(self):
		pass

	def __init_interface(self):
		pass


class StrategyFrame(IFRAME):
	def __init__(self, container):
		self.strategy_number = IntVar()
		super().__init__(container, border=30)
		self.__init_interface()

	def action_strategy(self):
		print(f"action_strategy: {self.strategy_number.get()}")
		self.ai.set_strategy(self.strategy_number.get())

	def __create_radio_strategy(self):
		list_strategy = self.ai.get_strategies()
		buttons = []

		for strategy in list_strategy:
			l = Radiobutton(self, text=strategy, variable=self.strategy_number, value=list_strategy[strategy], command=self.action_strategy)
			l.pack()
			buttons.append(l)

	def __init_interface(self):
		self.__create_radio_strategy()

	def update_interface(self):
		pass


class ButtonSystem(IFRAME):

	def __init__(self, container):
		super().__init__(container)
		self.__init_interface()

	@staticmethod
	def shutdown():
		os.system("sudo shutdown now")

	@staticmethod
	def reboot():
		os.system("sudo reboot")

	def close(self):
		self.parent.close()

	def create_button(self):
		Button(self, text="reboot", command=self.reboot).grid(row=0, column=1)
		Button(self, text="shutdown", command=self.shutdown).grid(row=0, column=2)
		Button(self, text="close", command=self.close).grid(row=0, column=3)

	def __init_interface(self):
		self.create_button()


class StatusFrame(IFRAME):

	def __init__(self, container):
		super().__init__(container)
		match_config = self.ai.cs.config.get_section('match')
		self.color1 = match_config['color1']
		self.color2 = match_config['color2']
		self.__init_interface()

	def create_color(self):
		self.change_color = Frame(self, relief="raised", background=self.ai.cs.match.get_color(), width=500, height=400)
		self.change_color.grid(column=5, row=5)

	def recalibration(self):
		self.ai.reset(True)

	def close(self):
		self.parent.close()

	def reset_match(self):
		try:
			self.ai.cs.match.reset_match()
		except Exception as e:
			print('[IA INTERFACE] Failed to reset match : %s' % str(e))

	def create_button(self):
		Button(self, text="Recalibaration", command=self.recalibration).grid(row=8, column=1)
		Button(self, text="Reset Match", command=self.reset_match).grid(row=8, column=1)
		Button(self, width=20, text="Change Color", command=self.action_color).grid(column=0, row=30)

	def __init_interface(self):
		self.create_color()
		self.create_button()

	def action_color(self):
		if self.ai.cs.match.get_color() == self.color1:
			self.ai.cs.match.set_color(self.color2)
			self.change_color.config(bg=self.color2)
		else:
			self.ai.cs.match.set_color(self.color1)
			self.change_color.config(bg=self.color1)


class MatchInterface(IFRAME):
	def __init__(self, container):
		super().__init__(container)
		self.__init_interface()

	def __init_interface(self):
		self.canvas = Canvas(self.parent.window, bg="orange", width=800, height=800)
		self.canvas.create_text(800/2, 450/2, text=f"Score: ")
		self.canvas.pack()

	def update_interface(self):
		pass


class AIInterface(Interface):
	def __init__(self, ai):
		self.ai = ai
		self.create_widget()
		super().__init__('AI')
		self.window.after(self.interface_refresh, self.update_interface)
		self.window.mainloop()

	def create_widget(self):
		self.strategies_frame = StrategyFrame(self)
		self.strategies_frame.config(bd=10)
		self.strategies_frame.pack()
		self.strategies_frame.place(height=40, width=150, x=0, y=200)

		self.button_system_frame = ButtonSystem(self)
		self.button_system_frame.pack()
		self.button_system_frame.place(height=29, width=213, x=480 / 2, y=0)

		self.status_frame = StatusFrame(self)
		self.status_frame.grid(row=1, column=1, columnspan=3, rowspan=5)
		self.status_frame.place(height=400, width=800, x=190, y=40)


	def update_interface(self):
		match_status = self.ai.cs.match.get_status()

		# self.bau_status_label.config(text='%s' % ' Bau Status: ON' if self.bau_status else 'Bau Status: OFF')
		if match_status["status"] == "Started":
			print("[+] Match is running")
		# self.color_label.config(text="Color: %s" % self.cs.match.get_color(), fg=self.cs.match.get_status()['color'])
		# self.score_label.config(text="Score: %d" % self.cs.match.get_status()['score'])
		# self.match_status_label.config(text="Match status: %s" % self.cs.match.get_status()['status'])
		# self.match_time_label.config(text="Match time: %d" % self.cs.match.get_status()['time'])
		# self.color_button.config(bg=self.cs.match.get_color())
		else:
			print("[+] Fix match not running or problem with this")
			self.status_frame.update_interface()
			self.button_system_frame.update_interface()
			self.strategies_frame.update_interface()

		# self.color_label.config(text="Color: %s" % 'M.C')
		# self.score_label.config(text="Score: %s" % 'M.C')
		# self.match_status_label.config(text="Match status: %s" % 'M.C')
		# self.match_time_label.config(text="Match time: %s" % 'M.C')

		self.window.after(self.interface_refresh, self.update_interface)

def main():
	if len(argv) > 1:
		global ROBOT
		ROBOT = argv[1]

if __name__ == "__main__":
	main()
