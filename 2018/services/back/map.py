#!/usr/bin/env python3

from cellaserv.service import Service
from cellaserv.proxy import CellaservProxy
from time import sleep
from threading import Thread, Lock

import urllib3

from evolutek.lib.graph import Graph
from evolutek.lib.settings import ROBOT

@Service.require("trajman", ROBOT)
class Map(Service):

    def __init__(self, server):
        super().__init__(ROBOT)
        self.server = server
        self.cs = CellaservProxy()
        self.create_graph()
        self.lock = Lock()
        self.thread = Thread(target=self.main_loop)
        self.thread.start()

    def create_graph(self):
        self.graph = Graph()
        color = self.cs.config.get(section='match', option='color')

        # Add nodes
        self.graph.insert_node('start', 500, 2760, color)
        self.graph.insert_node('bee', 1750, 2750, color)
        self.graph.insert_node('construction', 350, 2390, color)
        self.graph.insert_node('distrib1', 840, 2390, color)
        self.graph.insert_node('distrib2', 1550, 2390, color)
        self.graph.insert_node('interrupteur', 350, 1870, color)
        self.graph.insert_node('center_interrupter', 350, 1500, color)
        self.graph.insert_node('inter_a', 840, 1870, color)
        self.graph.insert_node('inter_b', 840, 1130, color)
        self.graph.insert_node('center_balls', 1550, 1500, color)
        self.graph.insert_node('center', 1000, 1500, color)
        self.graph.insert_node('distrib3', 840, 610, color)
        self.graph.insert_node('distrib4', 1550, 610, color)

        # Add edges
        self.graph.insert_edges('start', ['construction', 'distrib1', 'distrib4'])
        self.graph.insert_edges('bee', ['distrib2', 'inter_a', 'center_interrupter', 'center'])
        self.graph.insert_edges('construction', ['distrib1', 'interrupteur', 'distrib2', 'center_interrupter'])
        self.graph.insert_edges('distrib1', ['distrib2', 'inter_a', 'center', 'inter_b', 'distrib3'])
        self.graph.insert_edges('distrib2', ['inter_a', 'center', 'center_interrupter'])
        self.graph.insert_edges('interrupteur', ['center_interrupter', 'center_balls', 'inter_a', 'center', 'inter_b', 'distrib3', 'distrib4'])
        self.graph.insert_edges('center_interrupter', ['center_balls', 'inter_a', 'center', 'inter_b', 'distrib4'])
        self.graph.insert_edges('inter_a', ['center_balls', 'center', 'inter_b', 'distrib3', 'distrib4'])
        self.graph.insert_edges('inter_b', ['center_balls', 'center', 'distrib3', 'distrib4'])
        self.graph.insert_edges('center_balls', ['center'])
        self.graph.insert_edges('distrib3', ['distrib4', 'center'])
        self.graph.insert_edges('distrib4', ['center'])

    def main_loop(self):
        http = urllib3.PoolManager()
        while True:
            sleep(0.5)
            position = self.cs.trajman['pal'].get_position()
            print('Sending request to the server')
            r = http.request('POST', 'http://' + self.server + '/set_' + ROBOT,
                fields={'x' : position['x'],  'y' : position['y']})
            print(r.status)

    @Service.action
    def get_path(self, start, end):
        with self.lock:
            return self.graph.get_path(start, end)

    @Service.action
    def get_coords(self, point):
        with self.lock:
            return self.graph.nodes[point][0].to_dict()

def main():
    map = Map('localhost:4242')
    map.run()

if __name__ == "__main__":
    main()
