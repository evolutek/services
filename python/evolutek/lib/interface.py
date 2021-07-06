from os import _exit
from tkinter import *
from tkinter import Tk
from evolutek.lib.map.point import Point


class Interface:
	def __init__(self, title, nb_buttons_lines=0):
		self.window = Tk()
		self.window.bind('<Escape>', lambda e: self.close())
		self.window.title("%s Interface" % title)
		self.window.geometry("800x480")
		self.interface_refresh = 500
		self.start_match = False
		self.reset = False
		self.create_widget()
		self.update_interface()

	def create_widget(self):
		pass

	def update_interface(self):
		"""
		Updates the interface. This function can be overriden and
		will be called every interface_refresh milliseconds
		"""
		pass

	def _update_interface(self):
		# self.canvas.delete('background')
		# self.canvas.create_image(
		#     (3000 * self.interface_ratio) / 2,
		#     (2000 * self.interface_ratio) / 2,
		#     image=self.map,
		#     tag="background")
		self.window.after(self.interface_refresh, self._update_interface)
		self.update_interface()

	def loop(self):
		"""
		Starts the interface (displays it)
		Warning: This function is blocking and must be called in
		the same thread as the constructor of the interface.
		"""
		print('[INTERFACE] Window looping')
		self.window.mainloop()

	def close(self, signal_received=None, frame=None):
		print('[INTERFACE] Killing interface')
		self.window.destroy()
		_exit(0)


if __name__ == '__main__':
	interfaces = Interface("")
	interfaces.loop()
