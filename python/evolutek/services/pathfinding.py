#!/usr/bin/env python3

from math import sqrt
import sys

# Class for create point:
# all point have a cost (Empty, Obstacle, Border)
class Point:

	def __init__(self, x, y, cost):
		self.x = x
		self.y = y
		self.cost = cost

	def __str__(self):
		return str(self.x) + ", " + str(self.y)

class Robot:

	def __init__(self, x, y, robot_radius):
		self.x = x
		self.y = y
		self.robot_radius = robot_radius

	def SetPosition(self, x, y):
		self.x = x
		self.y = y

# Class for create obstacle :
# (x, y) is the center
# (x1, y1) and (x2, y2) is the two corner
class Obstacle:

	def __init__(self, x1, y1, x2, y2, tag):
		self.x = round((x1 + x2)/2)
		self.y = round((y1 + y2)/2)
		self.x1 = x1
		self.x2 = x2
		self.y1 = y1
		self.y2 = y2
		self.tag = tag

	def __str__(self):
		return self.tag + " (" + str(self.x1) + ", " + str(self.y1) + "), (" + str(self.x2) + ", " + str(self.y2) + ")"

# Class for create the map:
# w and h are the width and the hight
# Can set and remove obstacle in the map
class Map:

	def __init__(self, w, h, robot_radius, obstaclecost, emptycost, bordercost):
		self.w = w
		self.h = h
		self.ObstacleCost = obstaclecost
		self.EmptyCost = emptycost
		self.BorderCost = bordercost
		self.map = []
		for x in range (w+1):
			self.map.append([])
			for y in range(h+1):
				if(x == 0 or x == w+1 or y == 0 or y == h+1):
					if(x == 0 or x == w+1 or y == 0 or y == h+1):
						self.map[x].append(Point(x, y, BorderCost))
					else:
						self.map[x].append(Point(x, y, EmptyCost))
		self.robot_radius = robot_radius

	def SetObstacle(self, x, y):
		self.map[x][y].cost = self.ObstacleCost

	def RemoveObstacle(self, x, y):
		self.map[x][y].cost = self.EmptyCost
	
	def GetPoint(self, x, y):
		return self.map[x][y]

	# Return a point if it is in the map else return None
	def GetPointFromMap(self, x, y):
		valid = (x >= self.robot_radius
			and x <= self.w - self.robot_radius
			and y >= self.robot_radius
			and y <= self.h - self.robot_radius)
		return self.map[x][y] if valid else None

	# Return a list of the neighborhoods of a point of the map
	def GetNghbrs(self, x, y):
		N = []
		N.append(self.GetPointFormMap(x - 1, y))
		N.append(self.GetPointFormMap(x + 1, y))
		N.append(self.GetPointFormMap(x, y - 1))
		N.append(self.GetPointFormMap(x, y + 1))
		N.append(self.GetPointFormMap(x - 1, y - 1)) 
		N.append(self.GetPointFormMap(x - 1, y + 1))
		N.append(self.GetPointFormMap(x + 1, y - 1))
		N.append(self.GetPointFormMap(x - 1, y + 1))
		return [x for x in N if x is not None]
	
	# Return if the robot can access to a point
	def IsBlocked(self, x, y):
		if(x < self.robot_radius or
			x > (self.w - self.robot_radius) or
			y < self.robot-radius or
			y > self.h - self.robor_radius):
			return True;
		return self.map[x][y].cost != self.EmptyCost

    # Debug Part

	# Print all the map
	def PrintMap(self):
		for x in range(w+1):
			for y in range(h+1):
				if map[x][y].cost == EmptyCost:
					print(' ')
				elif map[x][y].cost == ObstacleCost:
					print('X')
				else:
					print('#')
    		print()

	# Create a .txt of the map
	def ExportMap(self):
		try:
			file.open('map.txt', 'w')
			for x in range(w+1):
				for y in range(h+1):
					if map[x][y].cost == EmptyCost:
						file.write(' ')
					elif map[x][y].cost == ObstacleCost:
						file.write('X')
					else:
						file.write('#')
				file.write('\n')
			file.close()
		except:
			print('Fail creating map.txt')
		
		
class Pathfinding:

	def __init__(self, mapw, maph, xrobot, yrobot, robot_radius):
		self.obstacles = []
		self.ObstacleCost = 10000
		self.EmptyCost = 0
		self.BorderCost = 99999
		self.map = Map(mapw, maph, robot_radius, ObstacleCost, EmptyCost, BorderCost)
		self.robot = Robot(xrobot, yrobot, robot_radius)

	def SetRobot(self, x, y):
		self.robot.SetPosition(x, y)

	def DistancePositionToPosition(self, x1, y1, x2, y2):
		return sqrt((x1 - x2)**2 + (y1 - y2)**2)

	def DistancePointToPoint(self, p1, p2):
		return self.DistancePositionToPosition(p1.x, p1.y, p2.x, p2.y)

	def DistancePointToRobot(sel, p):
		return self.DistancePositionToPosition(robot.x, robot.y, p.x, p.y)

	def AddRectangleObstacle(self, x, y, L, l, tag = "no tag"):
		self.obstacles.append(Obstacle(x - L, y - l, x + L, y - l, tag))
		for i in range(x, L):
			for j in range(y, l):
				self.map.SetObstacle(i, j)

	def AddSquareObstacle(self, x, y, height, tag = "no tag"):
		self.AddSquareObstacle(x - height, y - height, x + height, y + height, tag)

	def AddCricleObstacle(self, x, y, radius, tag = "not tag"):
		self.AddSquareObstacle(x, y, radius, tag)

	def RemoveObstacle(self, Obstacle):
		for i in range(x1, x2):
			for j in range(x1, x2):
				self.map.RemoveObstacle(i, j)

	def RemoveObstacleTag(self, tag):
		for obstacle in self.obstacles:
			if obstacle.tag == tag: 
				self.RemoveObstacle(obstacle)
				self.obstacles.remove(obstacle)

	def RemoveObstaclePosition(self, x, y, a = -1, b = -1):
		if a == -1 and b == -1:
			for obstacle in self.obstacles:
				if obstacle.x == x and obstacle.y == y:
					self.RemoveObstacle(obstacle)
					self.obstacles.remove(obstacle)
		else:
			for obstacle in self.obstacles:
				if obstacle.x1 == x and obstacle.y1 == y and obstacle.x2 == a and obstacle.y2 == b:
					self.RemoveObstacle(obstacle)
					self.obstacles.remove(obstacle)

	def ClearObstacles(self):
		self.obstacles.clear()

	def NoObstacleOnTheLineOsSight(self, p1, p2):
		pass

	# Debug Part
	def PrintObstacles(self):
		for obstacle in self.obstacles:
			print(str(obstacle))
