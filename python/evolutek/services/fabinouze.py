#!/usr/bin/env python3
from cellaserv.service import Service

class Fabinouze(Service):
    def __init__(self):
        super().__init__()

    @Service.action
    def get(self) -> str:
        return "I am not a pub!"


def main():
    inst = Fabinouze()
    inst.run()

if __name__ == "__main__":
    main()
