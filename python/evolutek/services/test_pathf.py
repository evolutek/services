import pathfinding

def main():
	pathf = pathfinding.Pathfinding(30, 20, 1)
	pathf.AddRectangleObstacle(8, 8, 12, 10)
	pathf.AddSquareObstacle(16, 16, 2)
	pathf.AddCircleObstacle(16, 3, 2)
	pathf.AddRectangleObstacle(12, 12, 19, 12)
	pathf.PrintObstacles()
	pathf.map.ExportMap()

if __name__ == '__main__':
	main()
