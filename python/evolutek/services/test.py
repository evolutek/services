#!/usr/bin/env python3

from cellaserv.service import Service

class Test(Service):
	def __init__(self):
		super().__init__()

	@Service.action
	def print_test(self, arg, arg2):
		return 40 + arg + arg2

	@Service.event
	def new_event(self):
		print("Votai Test.")

def main():
	inst = Test()
	inst.run()

if __name__ == "__main__":
	main()
