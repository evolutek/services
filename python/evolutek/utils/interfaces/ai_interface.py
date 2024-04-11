#!/usr/bin/python3

import os
from sys import argv

import tkinter as tk
import tkinter.font

from evolutek.lib.settings import ROBOT
from evolutek.lib.interface import Interface
from cellaserv.proxy import CellaservProxy


FONT_BIG = None
FONT_MEDIUM = None
FONT_SMALL = None


class IFrame(tk.Frame):
	def __init__(self, container, border=0):
		self.parent = container
		self.cs = container.cs
		super().__init__(self.parent.window, bd=border)

	def update_interface(self):
		pass

	def __init_interface(self):
		pass


class StrategyFrame(IFrame):
	def __init__(self, container):
		self.strategy_number = tk.IntVar()
		super().__init__(container)
		self.__init_interface()

	def action_strategy(self):
		self.cs.ai[ROBOT].set_strategy(self.strategy_number.get())
		print(f"New strategy: {self.cs.ai[ROBOT].get_strategies().keys(self.strategy_number.get())}")

	def __create_radio_strategy(self):
		list_strategy = self.cs.ai[ROBOT].get_strategies()
		buttons = []
		for strategy in list_strategy:
			l = tk.Radiobutton(
				self,
				text=strategy,
				variable=self.strategy_number,
				value=list_strategy[strategy],
				command=self.action_strategy,
				font=FONT_MEDIUM
			)
			l.pack(side=tk.TOP, fill=tk.X)
			buttons.append(l)

	def __init_interface(self):
		self.__create_radio_strategy()

	def update_interface(self):
		pass


class ButtonSystem(IFrame):
	def __init__(self, container):
		super().__init__(container)
		self.__init_interface()

	@staticmethod
	def shutdown():
		os.system("sudo reboot -p")

	@staticmethod
	def reboot():
		os.system("sudo reboot")

	def close(self):
		self.parent.close()

	def create_buttons(self):
		self.grid_columnconfigure(0, weight=1, uniform="c")
		self.grid_columnconfigure(1, weight=1, uniform="c")
		self.grid_columnconfigure(2, weight=1, uniform="c")
		tk.Button(self, text="Reboot", command=self.reboot, font=FONT_MEDIUM).grid(row=0, column=0, sticky=tk.N)
		tk.Button(self, text="Shutdown", command=self.shutdown, font=FONT_MEDIUM).grid(row=0, column=1, sticky=tk.N)
		tk.Button(self, text="Close", command=self.close, font=FONT_MEDIUM).grid(row=0, column=2, sticky=tk.N)

	def __init_interface(self):
		self.create_buttons()


class StatusFrame(IFrame):
	def __init__(self, container):
		super().__init__(container)
		self.color1 = self.cs.config.get('match', 'color1')
		self.color2 = self.cs.config.get('match', 'color2')
		self.__init_interface()

	def create_color(self):
		self.change_color = tk.Frame(self, relief="raised", background=self.cs.match.get_color(), width=500, height=400)
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

	def slurp(self):
		print("Bonjour slurping")
		self.cs.robot[ROBOT].fill_n_cherries(10)

	def slurp_less(self):
		print("Bonjour slurping un peu moins")
		self.cs.robot[ROBOT].fill_n_cherries(2)

	def slurp_set(self):
		print("Bonjour slurping le set")
		self.cs.robot[ROBOT].set_cherry_count()

	def create_buttons(self):
		tk.Button(self, text="Recalibrate", command=self.recalibration, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP)
		tk.Button(self, text="Reset position", command=self.reset_position, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP)
		tk.Button(self, text="Reset match", command=self.reset_match, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP)
		tk.Button(self, text="Change color", command=self.action_color, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP)

	def __init_interface(self):
		#self.create_color()
		self.create_buttons()

	def action_color(self):
		if self.cs.match.get_color() == self.color1:
			self.cs.match.set_color(self.color2)
			self.change_color.config(bg=self.color2)
		else:
			self.cs.match.set_color(self.color1)
			self.change_color.config(bg=self.color1)


class MatchInterface(IFrame):
	def __init__(self, container):
		super().__init__(container, bg=self.cs.match.get_color())
		self.__init_interface()

	def close(self):
		self.parent.close()

	def __init_interface(self):
		self.grid_rowconfigure(0, weight=1, uniform="r")
		self.grid_rowconfigure(1, weight=1, uniform="r")
		self.grid_rowconfigure(2, weight=1, uniform="r")
		tk.Button(self, text="Close", command=self.close, font=FONT_MEDIUM).grid(column=0, row=0, sticky=tk.NW)
		self.text = tk.Label(self, text=f"Score: 0", font=FONT_BIG)
		self.text.grid(column=0, row=1)

	def update_interface(self):
		match_status = self.cs.match.get_status()
		self.text.config(text=f"Score: {match_status['score']}")


class AIInterface(Interface):
	def __init__(self):
		self.cs = CellaservProxy()
		self.color = self.cs.match.get_color()
		super().__init__('AI')
		self.window.after(self.interface_refresh, self.update_interface)
		self.init_fonts()

	def init_fonts(self):
		global FONT_BIG, FONT_MEDIUM, FONT_SMALL
		FONT_BIG = tkinter.font.Font(size=36)
		FONT_MEDIUM = tkinter.font.Font(size=24)
		FONT_SMALL = tkinter.font.Font(size=16)

	def create_widget(self, start_match=False):
		if not start_match:
			self.button_system_frame = ButtonSystem(self)
			self.button_system_frame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=4, pady=4)

			self.strategies_frame = StrategyFrame(self)
			self.strategies_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=8, pady=8)

			self.status_frame = StatusFrame(self)
			self.status_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True, padx=8, pady=8)
		else:
			self.match_interfaces_frame = MatchInterface(self)
			self.match_interfaces_frame.pack(expand=True, fill=tk.BOTH)

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
