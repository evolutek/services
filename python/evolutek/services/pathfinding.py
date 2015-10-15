#!/usr/bin/env python3

# Example :
# import pathfinding
# pathf = Pathfinding(3000, 2000, 100)
# pathf.AddRectangleObstacle(200, 200, 100, 100)
# pathf.map.ExportMap()

from math import sqrt
import sys

# Class for create point:
# all point have a cost (Empty, Obstacle, Border)
class Point:

	def __init__(self, x, y, cost):
		self.x = x
		self.y = y
		self.cost = cost

	# Permite to convert a point to string
	def __str__(self):
		return str(self.x) + ", " + str(self.y)

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

	# Permite to convert an obstacle to string
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
		for x in range(0, self.h+1):
			self.map.append([])
			for y in range(0, self.w+1):
				if(x == 0 or x == h or y == 0 or y == w):
					self.map[x].append(Point(x, y, self.BorderCost))
				else:
					self.map[x].append(Point(x, y, self.EmptyCost))
		self.robot_radius = robot_radius

	# Set the cost of a cell to obstacle
	def SetObstacle(self, x, y):
		# print("set obstacle at point (" + str(x + 1) + ", " + str(y + 1) + ")")
		self.map[x][y].cost = self.ObstacleCost
	
	# Set the cost of a cell to empty
	def RemoveObstacle(self, x, y):
		self.map[x][y].cost = self.EmptyCost
	
	# Return a point of the map
	def GetPoint(self, y, x):
		return self.map[x][y]

	# Return a point if it is in the map else return None
	def GetPointFromMap(self, y, x):
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
	def IsBlocked(self, y, x):
		if(x < self.robot_radius or
			x > (self.w - self.robot_radius) or
			y < self.robot-radius or
			y > self.h - self.robor_radius):
			return True;
		return self.map[x][y].cost != self.EmptyCost

    # Debug Part

	# Print all the map
	def PrintMap(self):
		for x in range(self.h+1):
			for y in range(self.w+1):
				if self.map[x][y].cost == self.EmptyCost:
					print(' ')
				elif self.map[x][y].cost == self.ObstacleCost:
					print('X')
				else:
					print('#')
    		print()

	# Create a .txt of the map
	def ExportMap(self):
		fimap = open('map.txt', 'w')
		print("file create")
		for x in range(0,self.h+1):
			for y in range(0,self.w+1):
				if self.map[x][y].cost == self.EmptyCost:
					fimap.write(' ')
				elif self.map[x][y].cost == self.ObstacleCost:
					fimap.write('X')
				else:
					fimap.write('#')
			fimap.write('\n')
		fimap.close()

# Class to call to create an object pathfinding with a map with :
# The map weidth
# The map height
# The robot radius
class Pathfinding:

	def __init__(self, mapw, maph, robot_radius):
		self.obstacles = []
		self.ObstacleCost = 10000
		self.EmptyCost = 0
		self.BorderCost = 99999
		self.map = Map(mapw, maph, robot_radius, self.ObstacleCost, self.EmptyCost, self.BorderCost)

	# Compute the distance between two position
	def DistancePositionToPosition(self, x1, y1, x2, y2):
		return sqrt((x1 - x2)**2 + (y1 - y2)**2)

	# Compute the distance between two point
	def DistancePointToPoint(self, p1, p2):
		return self.DistancePositionToPosition(p1.x, p1.y, p2.x, p2.y)

	# Add a rectangular obstacle
	def AddRectangleObstacle(self, x1, y1, x2, y2, tag = "no tag"):
		self.obstacles.append(Obstacle(x1, y1, x2, y2, tag))
		for i in range(y1-1, y2):
			for j in range(x1-1, x2):
				self.map.SetObstacle(i, j)

	# Add a square obstacle
	def AddSquareObstacle(self, x, y, radius, tag = "no tag"):
		self.AddRectangleObstacle(x - (radius - 1), y - (radius - 1), x + (radius - 1), y + (radius - 1), tag)

	# Add a circle obstacle
	def AddCircleObstacle(self, x, y, radius, tag = "not tag"):
		self.AddSquareObstacle(x, y, radius, tag)

	# Remove an obstacle
	def RemoveObstacle(self, Obstacle):
		for i in range(y1-1, y2):
			for j in range(x1-1, x2):
				self.map.RemoveObstacle(i, j)

	# Rmove an obstacle with the tag
	def RemoveObstacleTag(self, tag):
		for obstacle in self.obstacles:
			if obstacle.tag == tag: 
				self.RemoveObstacle(obstacle)
				self.obstacles.remove(obstacle)

	# Remove an obstacle with the position
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

	# Remove all the obstacles of the list of obstacles
	def ClearObstacles(self):
		self.obstacles.clear()

	# Test if there is nos obstacle on the line of sight between two point
	def IfOnLineOfSight(self, p1, p2):
		pass

	# Debug Part

	# Print all the obstacles
	def PrintObstacles(self):
		for obstacle in self.obstacles:
			print(str(obstacle))

