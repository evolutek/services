#!/usr/bin/env python3

from math import sqrt

class Obstacle:

	def __init__(self, x1, y1, x2, y2, tag):
		self.x = (x1 + x2)/2
		self.y = (y1 + y2)/2
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.tag = tag
	
	def __str__(self):
        return self.tag + " (" + str(self.x1) + ", " + str(self.y1) + "), (" + str(self.x2) + ", " + str(self.y2) + ")"

class Map:

	def __init__(self, w, h, robot_radius, obstaclecost, emptycost):
		self.w = w
		self.h = h
		self.map = [[emptycost for n in range(w)] for n in range(h)]
		self.robot_radius = robot_radius
		self.ObstacleCost = obstaclecost
		self.EmptyCost = emptycost

	def SetObstacle(self, x, y):
		self.map[x][y] = self.ObstacleCost

	def RemoveObstacle(self, x, y):
		self.map[x][y] = self.emptycost

	def GetPoint(self, x, y):
		return self.map[x][y]

	def IsPointFromMap(self, x, y):
        valid = (x >= self.robot_radius
                and x <= self.w - self.robot_radius
                and y >= self.robot_radius
                and y <= self.h - self.robot_radius)
        return self.map[x][y] if valid else None

    # Debug Part

    def PrintMap(self):
    	for x in range(0, w):
    		for y in range(0, h):
    			print(map[x][y])
    		print()

class Pathfinding:

	def __init__(self, mapw, maph, robot_radius):
		self.obstacles = []
		self.ObstacleCost = 10000
		self.EmptyCost = 0
		self.map = Map(mapw, maph, robot_radius, ObstacleCost, EmptyCost)

	def AddRectangleObstacle(self, x, y, L, l, tag = "no tag"):
		self.obstacles.append(Obstacle(x - L, y - l, x + L, y - l, tag))
		for i in range(x, L):
			for j in range(y, l):
				map.SetObstacle(i, j)

	def AddSquareObstacle(self, x, y, height, tag = "no tag"):
		AddSquareObstacle(x - height, y - height, x + height, y + height, tag)

	def AddCricleObstacle(self, x, y, radius, tag = "not tag"):
		AddSquareObstacle(x, y, radius, tag)

	def RemoveObstacle(self, Obstacle):
		for i in range(x1, x2):
			for j range(x1, x2):
				map.RemoveObstacle(i, j)

	def RemoveObstacleTag(self, tag):
		for obstacle in self.obstacles:
			if obstacle.tag == tag: 
				RemoveObstacle(obstacle)
				self.obstacles.remove(obstacle)

	def RemoveObstaclePosition(self, x, y):
		for obstacle in self.obstacles:
			if obstacle.x = x and obstacle.y = y:
				RemoveObstacle(obstacle)
				self.obstacles.remove(obstacle)

	def ClearObstacles(self):
		self.obstacles.clear()

	# Debug Part

	def PrintObstacles(self):
    	for obstacle in self.obstacles:
    		print(str(obstacle))