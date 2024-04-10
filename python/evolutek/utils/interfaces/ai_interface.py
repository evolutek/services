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
	def __init__(self, root, parent, border=0, **kwargs):
		super().__init__(parent, bd=border, **kwargs)
		self.root = root

	def update_interface(self):
		pass

	def init_interface(self):
		pass


class StrategyFrame(IFrame):
	def __init__(self, root, parent):
		super().__init__(root, parent)
		self.strategy_number = tk.IntVar()
		self.init_interface()

	def change_strategy(self):
		self.root.cs.ai[ROBOT].set_strategy(self.strategy_number.get())
		print(f"New strategy: {self.root.cs.ai[ROBOT].get_strategies()[self.strategy_number.get()]}")

	def init_interface(self):
		list_strategy = self.root.cs.ai[ROBOT].get_strategies()
		for strategy in list_strategy:
			btn = tk.Radiobutton(
				self,
				text=strategy,
				variable=self.strategy_number,
				value=list_strategy[strategy],
				command=self.change_strategy,
				font=FONT_MEDIUM
			)
			btn.pack(side=tk.TOP, fill=tk.X)


class ButtonSystem(IFrame):
	def __init__(self, root, parent):
		super().__init__(root, parent)
		self.init_interface()

	@staticmethod
	def shutdown():
		os.system("sudo reboot -p")

	@staticmethod
	def reboot():
		os.system("sudo reboot")

	def close(self):
		self.root.close()

	def create_buttons(self):
		self.grid_columnconfigure(0, weight=1, uniform="c")
		self.grid_columnconfigure(1, weight=1, uniform="c")
		self.grid_columnconfigure(2, weight=1, uniform="c")
		tk.Button(self, text="Reboot", command=self.reboot, font=FONT_MEDIUM).grid(row=0, column=0, sticky=tk.N)
		tk.Button(self, text="Shutdown", command=self.shutdown, font=FONT_MEDIUM).grid(row=0, column=1, sticky=tk.N)
		tk.Button(self, text="Close", command=self.close, font=FONT_MEDIUM).grid(row=0, column=2, sticky=tk.N)

	def init_interface(self):
		self.create_buttons()


class StatusFrame(IFrame):
	def __init__(self, root, parent):
		super().__init__(root, parent)
		self.color1 = self.root.cs.config.get('match', 'color1')
		self.color2 = self.root.cs.config.get('match', 'color2')
		self.init_interface()

	def recalibration(self):
		self.root.cs.ai[ROBOT].reset(True)

	def close(self):
		self.root.close()

	def reset_position(self):
		self.root.cs.ai[ROBOT].reset(False)

	def reset_match(self):
		try:
			self.root.cs.match.end_match()
			self.root.cs.match.reset_match()
		except Exception as e:
			print('[IA INTERFACE] Failed to reset match : %s' % str(e))

	def init_interface(self):
		tk.Button(self, text="Recalibrate", command=self.recalibration, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP, pady=4)
		tk.Button(self, text="Reset position", command=self.reset_position, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP, pady=4)
		tk.Button(self, text="Reset match", command=self.reset_match, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP, pady=4)
		tk.Button(self, text="Change color", command=self.change_color, font=FONT_MEDIUM).pack(fill=tk.X, side=tk.TOP, pady=4)

	def change_color(self):
		if self.root.cs.match.get_color() == self.color1:
			self.root.cs.match.set_color(self.color2)
		else:
			self.root.cs.match.set_color(self.color1)


class HomeInterface(IFrame):
	def __init__(self, root, parent):
		super().__init__(root, parent)
		self.init_interface()

	def init_interface(self):
		self.grid_rowconfigure(0, weight=0)
		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.grid_columnconfigure(1, weight=1)

		self.button_system_frame = ButtonSystem(self.root, self)
		self.button_system_frame.grid(row=0, column=0, columnspan=2, padx=4, pady=4)

		self.strategies_frame = StrategyFrame(self.root, self)
		self.strategies_frame.grid(row=1, column=0, padx=8, pady=8)

		self.status_frame = StatusFrame(self.root, self)
		self.status_frame.grid(row=1, column=1, padx=8, pady=8)


class MatchInterface(IFrame):
	def __init__(self, root, parent):
		super().__init__(root, parent)
		self.init_interface()

	def reset(self):
		if self.root.match_status["status"] != "Started":
			self.root.cs.match.reset_match()
			self.root.cs.ai[ROBOT].reset(False)

	def stop(self):
		if self.root.match_status["status"] == "Started":
			self.root.cs.match.match_end()

	def init_interface(self):
		topbar = tk.Frame(self)
		topbar.pack(side=tk.TOP, fill=tk.X)
		tk.Button(topbar, text="Reset", command=self.reset, font=FONT_MEDIUM).pack(side=tk.LEFT)
		tk.Button(topbar, text="Stop", command=self.stop, font=FONT_MEDIUM).pack(side=tk.LEFT)
		self.text = tk.Label(self, text=f"Score: 0", font=FONT_BIG)
		self.text.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

	def update_interface(self):
		self.text.config(text=f"Score: {self.root.match_status['score']}")


class AIInterface(Interface):
	def __init__(self):
		super().__init__('AI')
		self.cs = CellaservProxy()
		self.init_fonts()
		#self.current_frame = None
		self.match_status = None

		self.container = tk.Frame(self.window)
		self.container.pack(side="top", fill="both", expand=True)
		self.container.grid_rowconfigure(0, weight=1)
		self.container.grid_columnconfigure(0, weight=1)

		self.match_interface = MatchInterface(self, self.container)
		self.home_interface = HomeInterface(self, self.container)
	
		self.match_interface.grid(row=0, column=0, sticky="nsew")
		self.home_interface.grid(row=0, column=0, sticky="nsew")

	def set_frame(self, frame):
		#if frame is self.current_frame:
		#	return
		#self.current_frame = frame
		frame.tkraise()

	def init_fonts(self):
		global FONT_BIG, FONT_MEDIUM, FONT_SMALL
		FONT_BIG = tkinter.font.Font(self.window, size=36)
		FONT_MEDIUM = tkinter.font.Font(self.window, size=24)
		FONT_SMALL = tkinter.font.Font(self.window, size=16)

	def update_interface(self):
		self.match_status = self.cs.match.get_status()
		self.window.configure(bd=5, highlightcolor=self.cs.match.get_color(), highlightthickness=5)
		if self.match_status["status"] == "Started" or self.match_status["status"] == "Ended":
			#print("[+] Match is running")
			self.set_frame(self.match_interface)
			self.match_interface.update_interface()
		else:
			#print("[+] Match is not running")
			self.set_frame(self.home_interface)
			self.home_interface.update_interface()


def main():
    if len(argv) > 1:
       global ROBOT
    interface = AIInterface()
    interface.loop()


if __name__ == "__main__":
	main()
