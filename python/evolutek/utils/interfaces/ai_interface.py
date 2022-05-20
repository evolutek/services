#!/usr/bin/python3

import os
import tkinter.font

from evolutek.lib.settings import ROBOT
from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
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
		self.cs = container.cs
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
		self.cs.ai[ROBOT].set_strategy(self.strategy_number.get())
		print(f"New strategy: {self.cs.ai[ROBOT].get_strategies().keys(self.strategy_number.get())}")

	def __create_radio_strategy(self):
		list_strategy = self.cs.ai[ROBOT].get_strategies()
		buttons = []

		for strategy in list_strategy:
			l = Radiobutton(self, text=strategy, variable=self.strategy_number, value=list_strategy[strategy],
							command=self.action_strategy)
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
		Button(self, text="reboot", command=self.reboot).grid(row=0, column=0)
		Button(self, text="shutdown", command=self.shutdown).grid(row=0, column=2)
		Button(self, text="close", command=self.close).grid(row=0, column=6)

	def __init_interface(self):
		self.create_button()


class StatusFrame(IFRAME):

	def __init__(self, container):
		super().__init__(container)
		self.color1 = self.cs.config.get('match', 'color1')
		self.color2 = self.cs.config.get('match', 'color2')
		self.__init_interface()

	def create_color(self):

		self.change_color = Frame(self, relief="raised", background=self.cs.match.get_color(), width=500, height=400)
		self.change_color.grid(column=5, row=5)

	def recalibration(self):
		print("Bonjour recalibration")
		self.cs.ai[ROBOT].reset(True)

	def close(self):
		self.parent.close()

	def reset_position(self):
		self.cs.ai[ROBOT].reset(False)

	def reset_match(self):
		try:
			self.cs.match.reset_match()
		except Exception as e:
			print('[IA INTERFACE] Failed to reset match : %s' % str(e))

	def create_button(self):
		Button(self, text="Recalibration", command=self.recalibration).grid(row=2, column=1)
		Button(self, text="set position", command=self.reset_position).grid(row=3, column=1)
		Button(self, text="Reset Match", command=self.reset_match).grid(row=4, column=1)
		Button(self, width=20, text="Change Color", command=self.action_color).grid(column=1, row=5)

	def __init_interface(self):
		#self.create_color()
		self.create_button()

	def action_color(self):
		if self.cs.match.get_color() == self.color1:
			self.cs.match.set_color(self.color2)
			self.change_color.config(bg=self.color2)
		else:
			self.cs.match.set_color(self.color1)
			self.change_color.config(bg=self.color1)


class MatchInterface(IFRAME):
	def __init__(self, container):
		super().__init__(container)
		self.__init_interface()

	def close(self):
		self.parent.close()

	def close(self):
		self.parent.close()

	def __init_interface(self):
		Button(self, text="Close", command=self.close).grid(row=0, column=0)
		self.canvas = Canvas(self.parent.window, bg=self.cs.match.get_color(), width=800, height=640)
		fonts = tkinter.font.Font(family='Helvetica', size=36, weight='bold')
		self.text = self.canvas.create_text(800 / 2, 480 / 2, text=f"Score: 0", font=fonts)
		self.canvas.pack()
		Button(self, text="close", command=self.close).grid(row=0, column=3)

	def update_interface(self):
		match_status = self.cs.match.get_status()
		self.canvas.itemconfig(self.text, text=f"Score: {match_status['score']}")


class AIInterface(Interface):
	def __init__(self):
		self.cs = CellaservProxy()
		self.color = self.cs.match.get_color()
		super().__init__('AI')
		self.window.after(self.interface_refresh, self.update_interface)

	def create_widget(self, start_match=False):
		if not start_match:
			self.strategies_frame = StrategyFrame(self)
			self.strategies_frame.config(bd=10)
			self.strategies_frame.pack()
			self.strategies_frame.place(height=150, width=250, x=0, y=100)

			self.button_system_frame = ButtonSystem(self)
			self.button_system_frame.pack()
			self.button_system_frame.place(height=29, width=213, x=480 / 2, y=0)

			self.status_frame = StatusFrame(self)
			self.status_frame.grid(row=1, column=2)
			self.status_frame.place(height=200, width=300, x=450, y=40)
		else:
			self.match_interfaces_frame = MatchInterface(self)
			self.match_interfaces_frame.pack()

	def update_interface(self):
		match_status = self.cs.match.get_status()
		self.window.configure(bd=5, highlightcolor=self.cs.match.get_color(), highlightthickness=5)
		if match_status["status"] == "Started" or match_status["status"] == "Ended":
			print("[+] Match is running")
			if not self.reset:
				self.status_frame.destroy()
				self.button_system_frame.destroy()
				self.strategies_frame.destroy()
				self.reset = True
				self.create_widget(True)
			else:
				self.match_interfaces_frame.update_interface()
		else:
			print("[+] Fix match not running or problem with this")
			if not self.reset:
				self.status_frame.update_interface()
				self.button_system_frame.update_interface()
				self.strategies_frame.update_interface()
			else:
				self.reset = False
				self.create_widget()
				self.match_interfaces_frame.destroy()
		self.window.after(self.interface_refresh, self.update_interface)


def main():
    if len(argv) > 1:
       global ROBOT
    interface = AIInterface()
    interface.window.configure(bd=0)
    interface.loop()

if __name__ == "__main__":
	main()
